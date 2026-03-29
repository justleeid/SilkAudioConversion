"""
上传相关数据模型
"""
from typing import List
from pydantic import BaseModel
from app.models.convert import FileInfo


class UploadResponse(BaseModel):
    """上传响应"""

    files: List[FileInfo]


class FileValidationResult(BaseModel):
    """文件验证结果"""

    is_valid: bool
    error_message: str = ""
