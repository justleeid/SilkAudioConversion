"""
文件上传服务
参考 development.md 第 6.1 节、PRD.md 第 2.1.1 节
"""
import uuid
from pathlib import Path
from typing import List
from fastapi import UploadFile
from app.config import settings
from app.logger import logger
from app.utils.path_security import get_safe_path, sanitize_filename
from app.models.upload import FileValidationResult
from app.models.convert import FileInfo

# 简单的文件类型检测（基于文件头）
def detect_file_type(content: bytes) -> str:
    """基于文件头检测文件类型"""
    silk_header_lower = content[:10].lower()
    if (silk_header_lower.startswith(b'\x02#!silk_v3') or
            content[:9].lower().startswith(b'#!silk_v3')):
        return 'audio/silk'
    elif content.startswith(b'RIFF') and b'WAVE' in content[:12]:
        return 'audio/wav'
    elif content.startswith(b'\xff\xfb') or content.startswith(b'ID3'):
        return 'audio/mpeg'
    elif content.startswith(b'#!AMR'):
        return 'audio/amr'
    elif len(content) >= 12 and content[4:8] == b'ftyp':
        return 'audio/mp4'
    return 'application/octet-stream'


class FileService:
    """文件上传处理服务"""

    ALLOWED_EXTENSIONS = {'.silk', '.wav', '.mp3', '.amr', '.m4a'}
    ALLOWED_MIME_TYPES = {
        'audio/x-silk', 'audio/silk',
        'audio/wav', 'audio/x-wav', 'audio/wave',
        'audio/mpeg', 'audio/mp3',
        'audio/amr', 'audio/x-amr'
        , 'audio/mp4', 'audio/m4a', 'audio/x-m4a'
    }

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.max_file_size = settings.max_file_size
        self.max_file_count = settings.max_file_count

        # 确保上传目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> FileValidationResult:
        """
        验证上传文件

        Args:
            file: 上传的文件对象

        Returns:
            验证结果
        """
        try:
            # 1. 检查文件扩展名
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.ALLOWED_EXTENSIONS:
                logger.warning(f"不支持的文件扩展名: {file_ext}")
                return FileValidationResult(
                    is_valid=False,
                    error_message=f"不支持的文件格式: {file_ext}"
                )

            # 2. 检查文件大小
            # FastAPI 的 UploadFile 没有 size 属性，需要通过其他方式获取
            # 这里先读取内容进行验证
            content = file.file.read()
            file.file.seek(0)  # 重置文件指针

            file_size = len(content)
            if file_size > self.max_file_size:
                size_mb = file_size / (1024 * 1024)
                max_mb = self.max_file_size / (1024 * 1024)
                logger.warning(f"文件过大: {size_mb:.2f}MB > {max_mb:.0f}MB")
                return FileValidationResult(
                    is_valid=False,
                    error_message=f"文件过大，最大 {max_mb:.0f}MB"
                )

            # 3. 检查文件魔数（MIME 类型）
            file_type = detect_file_type(content[:1024])

            # 验证文件类型
            if not any(t in file_type for t in self.ALLOWED_MIME_TYPES):
                logger.warning(f"文件内容与扩展名不匹配: {file_type}")
                return FileValidationResult(
                    is_valid=False,
                    error_message=f"文件内容与扩展名不匹配"
                )

            logger.info(f"✅ 文件验证通过: {file.filename}")
            return FileValidationResult(is_valid=True)

        except Exception as e:
            logger.error(f"文件验证失败: {str(e)}")
            return FileValidationResult(
                is_valid=False,
                error_message=f"文件验证失败: {str(e)}"
            )

    async def save_upload(self, file: UploadFile) -> FileInfo:
        """
        保存上传文件

        Args:
            file: 上传的文件对象

        Returns:
            文件信息
        """
        try:
            # 生成唯一任务 ID
            task_id = uuid.uuid4().hex

            # 清理文件名
            safe_filename = sanitize_filename(file.filename)

            # 生成安全路径
            file_path = get_safe_path(self.upload_dir, f"{task_id}_{safe_filename}")

            # 保存文件
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)

            # 获取文件格式
            file_ext = Path(file.filename).suffix.lower().replace('.', '')

            logger.info(f"✅ 文件保存成功: {file_path}")

            return FileInfo(
                task_id=task_id,
                filename=file.filename,
                size=len(content),
                format=file_ext.upper()
            )

        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            raise

    async def upload_and_validate(
        self,
        files: List[UploadFile]
    ) -> List[FileInfo]:
        """
        批量上传并验证文件

        Args:
            files: 上传文件列表

        Returns:
            验证通过的文件信息列表
        """
        if len(files) > self.max_file_count:
            raise ValueError(f"文件数量超过限制: {self.max_file_count}")

        validated_files = []

        for file in files:
            # 验证文件
            result = self.validate_file(file)

            if not result.is_valid:
                logger.warning(f"文件验证失败: {file.filename} - {result.error_message}")
                continue

            # 保存文件
            file_info = await self.save_upload(file)
            validated_files.append(file_info)

        logger.info(f"✅ 成功上传 {len(validated_files)}/{len(files)} 个文件")
        return validated_files
