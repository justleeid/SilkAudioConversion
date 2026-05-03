"""
统一 API 响应模型
参考 development.md 第 4.2.2 节
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""

    code: int          # 0 成功，其他值为错误码
    message: str       # 成功或错误消息
    data: Optional[T] = None


# 错误码定义
class ErrorCode:
    """错误码枚举"""
    SUCCESS = 0
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    FILE_TOO_LARGE = 413
    INTERNAL_ERROR = 500
    INVALID_SILK_HEADER = 1001
    UNSUPPORTED_FORMAT = 1002
    CONVERSION_FAILED = 1003


# 错误消息映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.BAD_REQUEST: "请求参数错误",
    ErrorCode.UNAUTHORIZED: "未授权",
    ErrorCode.FORBIDDEN: "禁止访问",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.FILE_TOO_LARGE: "文件过大",
    ErrorCode.INTERNAL_ERROR: "服务器错误",
    ErrorCode.INVALID_SILK_HEADER: "无效的 SILK 文件头",
    ErrorCode.UNSUPPORTED_FORMAT: "不支持的文件格式",
    ErrorCode.CONVERSION_FAILED: "转换失败",
}