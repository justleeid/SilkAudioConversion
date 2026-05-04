"""
暂存区管理服务
参考 PRD.md 第 2.1.5 节
"""
import os
import time
import asyncio
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.config import settings
from app.logger import logger


class StagingFile(BaseModel):
    """暂存区文件信息"""
    file_id: str
    original_name: str
    output_name: str
    size: int
    created_at: str
    expires_at: str
    download_url: str


class StagingService:
    """暂存区管理服务（单例）"""

    _instance: Optional['StagingService'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.staging_dir = Path(settings.output_dir)
        self.expire_hours = settings.cache_expire_hours
        self.cleanup_interval = settings.cache_cleanup_interval
        self.staging_dir.mkdir(parents=True, exist_ok=True)

        # 记录文件元数据
        self._metadata: Dict[str, dict] = {}

        # 启动后台清理任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = True

    async def start_cleanup_task(self):
        """启动后台清理任务"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("暂存区后台清理任务已启动")

    async def _cleanup_loop(self):
        """后台清理循环"""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            await self.cleanup_expired()

    async def add_file(
        self,
        file_id: str,
        original_name: str,
        output_path: Path
    ) -> StagingFile:
        """添加文件到暂存区"""
        now = datetime.now()
        expires = now + timedelta(hours=self.expire_hours)
        size = output_path.stat().st_size if output_path.exists() else 0

        # 生成用户友好的输出文件名
        import os
        original_base = os.path.splitext(original_name)[0]
        output_ext = output_path.suffix
        friendly_output_name = f"{original_base}_converted{output_ext}"

        staging_file = StagingFile(
            file_id=file_id,
            original_name=original_name,
            output_name=friendly_output_name,
            size=size,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            download_url=f"/api/download/{file_id}"
        )

        self._metadata[file_id] = staging_file.model_dump()
        return staging_file

    def get_file(self, file_id: str) -> Optional[StagingFile]:
        """获取暂存文件信息"""
        self._sync_metadata_with_disk()
        data = self._metadata.get(file_id)
        if data:
            return StagingFile(**data)
        return None

    def list_files(self) -> List[StagingFile]:
        """列出所有暂存文件"""
        self._sync_metadata_with_disk()
        return [StagingFile(**data) for data in self._metadata.values()]

    def _sync_metadata_with_disk(self) -> None:
        """将内存元数据与磁盘输出目录同步，避免重启后列表为空。"""
        now = datetime.now()

        # 仅识别标准输出命名: {file_id}_output.{ext}
        output_files = list(self.staging_dir.glob("*_output.*"))
        disk_map: Dict[str, Path] = {}
        for file_path in output_files:
            stem = file_path.stem
            if stem.endswith("_output"):
                file_id = stem[:-7]
                if file_id:
                    disk_map[file_id] = file_path

        # 删除内存中已不存在的文件记录
        stale_ids = [fid for fid in self._metadata.keys() if fid not in disk_map]
        for fid in stale_ids:
            self._metadata.pop(fid, None)

        # 新增或修复元数据
        for file_id, file_path in disk_map.items():
            stat = file_path.stat()
            created_at = datetime.fromtimestamp(stat.st_mtime)
            expires_at = created_at + timedelta(hours=self.expire_hours)

            existing = self._metadata.get(file_id)
            if existing:
                existing["size"] = stat.st_size
                existing["output_name"] = existing.get("output_name") or file_path.name
                existing["download_url"] = f"/api/download/{file_id}"
                existing["created_at"] = existing.get("created_at") or created_at.isoformat()
                existing["expires_at"] = existing.get("expires_at") or expires_at.isoformat()
            else:
                self._metadata[file_id] = {
                    "file_id": file_id,
                    "original_name": file_path.name,
                    "output_name": file_path.name,
                    "size": stat.st_size,
                    "created_at": created_at.isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "download_url": f"/api/download/{file_id}",
                }

    def delete_file(self, file_id: str) -> bool:
        """删除暂存文件"""
        try:
            # 删除文件
            for f in self.staging_dir.glob(f"{file_id}_*"):
                f.unlink()

            # 删除元数据
            self._metadata.pop(file_id, None)
            logger.info(f"暂存文件已删除: {file_id}")
            return True
        except Exception as e:
            logger.error(f"删除暂存文件失败: {str(e)}")
            return False

    async def cleanup_expired(self) -> int:
        """清理过期文件，返回清理数量"""
        now = datetime.now()
        expired_ids = []

        for file_id, data in self._metadata.items():
            expires_at = datetime.fromisoformat(data['expires_at'])
            if now > expires_at:
                expired_ids.append(file_id)

        for file_id in expired_ids:
            self.delete_file(file_id)

        if expired_ids:
            logger.info(f"暂存区清理: 删除 {len(expired_ids)} 个过期文件")

        return len(expired_ids)

    def get_total_size(self) -> int:
        """获取暂存区总大小"""
        total = 0
        for data in self._metadata.values():
            total += data.get('size', 0)
        return total

    def get_stats(self) -> dict:
        """获取暂存区统计信息"""
        files = self.list_files()
        return {
            "file_count": len(files),
            "total_size": sum(f.size for f in files),
            "expire_hours": self.expire_hours,
            "cleanup_interval": self.cleanup_interval
        }
