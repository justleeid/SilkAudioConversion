"""
暂存区管理服务
参考 PRD.md 第 2.1.5 节
"""
import os
import time
import asyncio
import shutil
import re
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

        # 记录文件元数据（内存 + 磁盘持久化）
        self._metadata: Dict[str, dict] = {}
        self._metadata_file = self.staging_dir / ".staging_metadata.json"

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

    def _save_metadata(self):
        """将内存元数据持久化到磁盘 JSON 文件"""
        try:
            import json
            with open(self._metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存暂存区元数据失败: {str(e)}")

    @staticmethod
    def _strip_task_prefixes(filename: str) -> str:
        """去除文件名里前置的一个或多个 32 位 hex 任务前缀。"""
        name = filename
        pattern = re.compile(r"^[0-9a-fA-F]{32}_")
        while pattern.match(name):
            name = name[33:]
        return name

    @staticmethod
    def _is_generic_name(name: Optional[str]) -> bool:
        """判断是否为无业务意义的通用名（如 output.silk）。"""
        if not name:
            return True
        lower_name = name.lower()
        return lower_name in {
            "output.silk",
            "output.wav",
            "output.mp3",
            "output.amr",
            "output.m4a",
            "output.plist",
            "output_converted.silk",
            "output_converted.wav",
            "output_converted.mp3",
            "output_converted.amr",
            "output_converted.m4a",
            "output_converted.plist",
        }

    def _infer_better_name_from_file_id(self, file_id: str) -> Optional[str]:
        """根据复合 file_id 回溯上传目录，尽量推断用户可读名称。"""
        if "_" not in file_id:
            return None

        upload_dir = self.staging_dir.parent / "uploads"
        if not upload_dir.exists():
            return None

        parts = file_id.split("_")
        # 复合 id 常见形态: {new_id}_{old_id}，优先从后面的 id 反查
        for candidate_id in reversed(parts[1:]):
            if not re.fullmatch(r"[0-9a-fA-F]{32}", candidate_id):
                continue
            for f in upload_dir.iterdir():
                if not f.is_file():
                    continue
                if f.name.startswith(candidate_id + "_"):
                    raw_name = f.name[len(candidate_id) + 1:]
                    normalized = self._strip_task_prefixes(raw_name)
                    if not self._is_generic_name(normalized):
                        return normalized
        return None

    def _load_metadata(self):
        """从磁盘 JSON 文件恢复元数据（仅在内存为空时调用）"""
        if not self._metadata_file.exists():
            return
        try:
            import json
            with open(self._metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._metadata.update(data)
                logger.info(f"从磁盘恢复暂存区元数据: {len(data)} 条记录")
        except Exception as e:
            logger.error(f"加载暂存区元数据失败: {str(e)}")

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

        # 生成用户友好的输出文件名（去除历史任务前缀）
        import os
        normalized_original_name = self._strip_task_prefixes(original_name)
        original_base = os.path.splitext(normalized_original_name)[0]
        output_ext = output_path.suffix
        friendly_output_name = f"{original_base}{output_ext}"

        staging_file = StagingFile(
            file_id=file_id,
            original_name=normalized_original_name,
            output_name=friendly_output_name,
            size=size,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            download_url=f"/api/download/{file_id}"
        )

        self._metadata[file_id] = staging_file.model_dump()
        self._save_metadata()
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
        # 首次调用时从磁盘恢复持久化的元数据
        if not self._metadata:
            self._load_metadata()

        now = datetime.now()

        # 递归识别标准输出命名: {file_id}_output.{ext}，支持子目录（例如解压后的文件夹）
        output_files = list(self.staging_dir.glob("**/*_output.*"))
        disk_map: Dict[str, Path] = {}
        for file_path in output_files:
            stem = file_path.stem
            if stem.endswith("_output"):
                file_id = stem[:-7]
                if file_id:
                    disk_map[file_id] = file_path

        # 尝试从上传目录匹配原始文件名（仅补全缺少 original_name 的记录）
        upload_dir = self.staging_dir.parent / "uploads"
        upload_name_map: Dict[str, str] = {}
        if upload_dir.exists():
            for f in upload_dir.iterdir():
                if f.is_file():
                    name = f.name
                    for fid in disk_map:
                        if name.startswith(fid + "_"):
                            upload_name_map[fid] = self._strip_task_prefixes(name[len(fid) + 1:])
                            break

        # 删除内存中已不存在的文件记录
        stale_ids = [fid for fid in self._metadata.keys() if fid not in disk_map]
        for fid in stale_ids:
            self._metadata.pop(fid, None)
        if stale_ids:
            self._save_metadata()

        # 新增或修复元数据
        changed = False
        for file_id, file_path in disk_map.items():
            stat = file_path.stat()
            created_at = datetime.fromtimestamp(stat.st_mtime)
            expires_at = created_at + timedelta(hours=self.expire_hours)

            # 计算基于磁盘文件名的显示名称
            import os
            if file_id in upload_name_map:
                base = os.path.splitext(upload_name_map[file_id])[0]
                ext = file_path.suffix
                disk_display_name = f"{base}{ext}"
            else:
                fmt = file_path.suffix.lstrip('.').upper()
                disk_display_name = f"converted_{file_id[:8]}.{fmt}"

            existing = self._metadata.get(file_id)
            if existing:
                existing["size"] = stat.st_size
                inferred_name = self._infer_better_name_from_file_id(file_id)
                current_original = existing.get("original_name")
                current_output = existing.get("output_name")

                if self._is_generic_name(current_original):
                    if inferred_name:
                        existing["original_name"] = inferred_name
                        changed = True
                    elif file_id in upload_name_map:
                        existing["original_name"] = upload_name_map[file_id]
                        changed = True

                if self._is_generic_name(current_output):
                    source_name = existing.get("original_name") or inferred_name or upload_name_map.get(file_id)
                    if source_name:
                        base = os.path.splitext(source_name)[0]
                        existing["output_name"] = f"{base}{file_path.suffix}"
                        changed = True

                # 优先保留已有的友好名称，否则使用从磁盘还原的名称
                existing["output_name"] = existing.get("output_name") or disk_display_name
                existing["original_name"] = existing.get("original_name") or upload_name_map.get(file_id, disk_display_name)
                existing["download_url"] = f"/api/download/{file_id}"
                existing["created_at"] = existing.get("created_at") or created_at.isoformat()
                existing["expires_at"] = existing.get("expires_at") or expires_at.isoformat()
            else:
                inferred_name = self._infer_better_name_from_file_id(file_id)
                original_name = inferred_name or upload_name_map.get(file_id, disk_display_name)
                original_name = self._strip_task_prefixes(original_name)
                base = os.path.splitext(original_name)[0]
                output_name = f"{base}{file_path.suffix}" if not self._is_generic_name(original_name) else disk_display_name
                self._metadata[file_id] = {
                    "file_id": file_id,
                    "original_name": original_name,
                    "output_name": output_name,
                    "size": stat.st_size,
                    "created_at": created_at.isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "download_url": f"/api/download/{file_id}",
                }
                changed = True

        if changed:
            self._save_metadata()

    def rename_file(self, file_id: str, new_name: str) -> bool:
        """重命名暂存文件（仅更新元数据中的显示名称）"""
        self._sync_metadata_with_disk()
        data = self._metadata.get(file_id)
        if not data:
            return False

        # 保留原始扩展名
        import os
        current_name = data.get('output_name') or data.get('original_name', '')
        _, ext = os.path.splitext(current_name)
        if ext and not new_name.lower().endswith(ext.lower()):
            new_name = new_name + ext

        data['output_name'] = new_name
        data['original_name'] = new_name
        self._save_metadata()
        logger.info(f"暂存文件已重命名: {file_id} -> {new_name}")
        return True

    def resolve_original_name(self, file_id: str) -> Optional[str]:
        """根据 file_id 解析原始文件名（优先内存元数据，其次上传目录文件名）"""
        # 优先从已保存的元数据获取
        data = self._metadata.get(file_id)
        if data and data.get('original_name'):
            return self._strip_task_prefixes(data['original_name'])

        # 其次尝试从上传目录解析
        upload_dir = self.staging_dir.parent / "uploads"
        if upload_dir.exists():
            for f in upload_dir.iterdir():
                if f.is_file() and f.name.startswith(file_id + "_"):
                    return self._strip_task_prefixes(f.name[len(file_id) + 1:])
        return None

    def delete_file(self, file_id: str) -> bool:
        """删除暂存文件"""
        try:
            # 删除文件
            for f in self.staging_dir.glob(f"{file_id}_*"):
                f.unlink()

            # 删除元数据
            self._metadata.pop(file_id, None)
            self._save_metadata()
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
