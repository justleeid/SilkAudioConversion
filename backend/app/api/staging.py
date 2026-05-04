"""
暂存区 API 路由
参考 PRD.md 第 5.6 节
"""
from fastapi import APIRouter
from app.models.response import ApiResponse, ErrorCode
from app.services.staging_service import StagingService
from app.logger import logger

router = APIRouter(prefix="/api/staging", tags=["staging"])

staging_service = StagingService()


@router.get("", response_model=ApiResponse)
async def list_staging():
    """查看暂存区文件列表"""
    try:
        files = staging_service.list_files()
        stats = staging_service.get_stats()

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message="查询成功",
            data={
                "files": [f.model_dump() for f in files],
                "stats": stats
            }
        )

    except Exception as e:
        logger.error(f"查询暂存区失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )


@router.delete("/{file_id}", response_model=ApiResponse)
async def delete_staging_file(file_id: str):
    """删除暂存文件"""
    try:
        success = staging_service.delete_file(file_id)

        if not success:
            return ApiResponse(
                code=ErrorCode.NOT_FOUND,
                message="文件不存在或删除失败"
            )

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message="文件已删除"
        )

    except Exception as e:
        logger.error(f"删除暂存文件失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )


@router.post("/cleanup", response_model=ApiResponse)
async def manual_cleanup():
    """手动清理过期文件"""
    try:
        count = await staging_service.cleanup_expired()

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message=f"已清理 {count} 个过期文件",
            data={"cleaned": count}
        )

    except Exception as e:
        logger.error(f"清理暂存区失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )
