"""
文件上传和验证服务
参考 development.md 第 4.2.1 节、PRD.md 第 2.1.1 节
"""
import uuid
import mimetypes
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
from app.config import settings
from app.logger import logger


class FileValidationResult(BaseModel):
    """文件验证结果"""
    task_id: str
    filename: str
    file_size: int
    file_type: str


class FileInfo(BaseModel):
    """文件信息"""
    task_id: str
    filename: str
    file_size: int
    file_type: str
    upload_url: str


class FileService:
    """文件服务"""

    # 支持的文件扩展名
    ALLOWED_EXTENSIONS = {'.silk', '.wav', '.mp3', '.amr', '.m4a'}

    # 支持的 MIME 类型
    ALLOWED_MIME_TYPES = {
        'audio/silk',
        'audio/x-silk',
        'audio/wav',
        'audio/x-wav',
        'audio/mpeg',
        'audio/mp3',
        'audio/amr',
        'audio/amr-wb',
        'audio/mp4',  # for M4A
    }

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def detect_file_type(self, file_path: Path) -> str:
        """
        检测文件类型

        Args:
            file_path: 文件路径

        Returns:
            文件类型（扩展名或 MIME 类型）
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)

            # SILK 格式检测
            if header.startswith(b'\x02#!SILK_V3'):  # 微信格式
                return 'audio/silk'
            if header.startswith(b'#!SILK_V3'):  # 标准格式
                return 'audio/silk'

            # WAV 格式检测
            if header.startswith(b'RIFF') and b'WAVE' in header:
                return 'audio/wav'

            # MP3 格式检测
            if header.startswith(b'\xff\xfb') or header.startswith(b'ID3'):
                return 'audio/mpeg'

            # AMR 格式检测
            if header.startswith(b'#!AMR'):
                return 'audio/amr'

            # M4A/MP4 格式检测（ftyp signature at offset 4-8）
            if len(header) >= 12 and header[4:8] == b'ftyp':
                return 'audio/mp4'

            # 默认使用系统识别
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or 'application/octet-stream'

        except Exception as e:
            logger.warning(f"文件类型检测失败: {str(e)}")
            return 'application/octet-stream'

    def validate_file(self, file_path: Path) -> bool:
        """
        验证文件

        Args:
            file_path: 文件路径

        Returns:
            是否验证通过
        """
        # 检查扩展名
        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            logger.warning(f"不支持的文件扩展名: {file_path.suffix}")
            return False

        # 检查文件类型
        file_type = self.detect_file_type(file_path)
        if file_type not in self.ALLOWED_MIME_TYPES:
            logger.warning(f"不支持的 MIME 类型: {file_type}")
            return False

        # 检查文件大小
        file_size = file_path.stat().st_size
        max_size = settings.max_upload_size
        if file_size > max_size:
            logger.warning(f"文件过大: {file_size} > {max_size}")
            return False

        return True

    async def upload_and_validate(self, files: list) -> List[FileInfo]:
        """
        上传并验证文件

        Args:
            files: 上传文件列表（FastAPI UploadFile 对象）

        Returns:
            验证成功的文件信息列表

        Raises:
            Exception: 上传失败
        """
        validated_files = []

        for file in files:
            try:
                # 生成任务 ID
                task_id = str(uuid.uuid4())

                # 保存文件
                file_path = self.upload_dir / f"{task_id}_{file.filename}"
                content = await file.read()

                with open(file_path, 'wb') as f:
                    f.write(content)

                logger.info(f"文件已上传: {file_path}")

                # 验证文件
                if not self.validate_file(file_path):
                    file_path.unlink()
                    logger.error(f"文件验证失败: {file.filename}")
                    raise ValueError(f"不支持的文件格式: {file.filename}")

                # 获取文件类型
                file_type = self.detect_file_type(file_path)
                file_size = file_path.stat().st_size

                file_info = FileInfo(
                    task_id=task_id,
                    filename=file.filename,
                    file_size=file_size,
                    file_type=file_type,
                    upload_url=f"/api/download/{task_id}"
                )

                validated_files.append(file_info)

                logger.info(f"✅ 文件验证成功: {file.filename} (task_id: {task_id})")

            except Exception as e:
                logger.error(f"❌ 文件上传失败: {file.filename} - {str(e)}")
                raise

        return validated_files
