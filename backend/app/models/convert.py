"""
转换相关数据模型
参考 PRD.md 第 5.2 节
"""
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TargetFormat(str, Enum):
    """目标格式枚举"""
    WAV = "WAV"
    MP3 = "MP3"
    SILK = "SILK"
    PLIST = "PLIST"


class ConvertRequest(BaseModel):
    """转换请求参数"""

    target_format: TargetFormat
    wechat_compatible: bool = True
    sample_rate: Optional[int] = 24000
    bit_rate: Optional[int] = 24000
    frame_size: Optional[int] = 20


class FileInfo(BaseModel):
    """文件信息"""

    task_id: str
    filename: str
    size: int
    format: str


class TaskInfo(BaseModel):
    """任务信息"""

    task_id: str
    status: TaskStatus
    progress: int = 0
    estimated_time: Optional[int] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None