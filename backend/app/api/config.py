"""
配置 API 路由
参考 PRD.md 第 5.7 节
"""
from fastapi import APIRouter
from app.models.response import ApiResponse, ErrorCode
from app.config import settings
from app.logger import logger

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=ApiResponse)
async def get_config():
    """获取当前配置"""
    try:
        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message="查询成功",
            data={
                "supported_formats": [".silk", ".wav", ".mp3", ".amr", ".m4a"],
                "max_file_size": settings.max_file_size,
                "max_file_count": settings.max_file_count,
                "sample_rates": [8000, 16000, 24000, 44100],
                "bit_rates": [12000, 16000, 24000, 32000],
                "frame_sizes": [20, 40, 60],
                "cache_expire_hours": settings.cache_expire_hours,
                "max_concurrent_tasks": settings.max_concurrent_tasks
            }
        )
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )
