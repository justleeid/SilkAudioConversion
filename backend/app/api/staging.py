"""
暂存区 API 路由
参考 PRD.md 第 5.6 节
"""
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app.models.response import ApiResponse, ErrorCode
from app.services.staging_service import StagingService
from app.logger import logger

router = APIRouter(prefix="/api/staging", tags=["staging"])

staging_service = StagingService()


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    file_ids: List[str]


class RenameRequest(BaseModel):
    """重命名请求"""
    name: str


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


@router.post("/batch-delete", response_model=ApiResponse)
async def batch_delete_staging_files(request: BatchDeleteRequest):
    """批量删除暂存文件"""
    try:
        if not request.file_ids:
            return ApiResponse(
                code=ErrorCode.BAD_REQUEST,
                message="请提供要删除的文件 ID 列表"
            )

        deleted = 0
        for file_id in request.file_ids:
            if staging_service.delete_file(file_id):
                deleted += 1

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message=f"已删除 {deleted} 个文件",
            data={"deleted": deleted}
        )

    except Exception as e:
        logger.error(f"批量删除暂存文件失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )


@router.post("/{file_id}/rename", response_model=ApiResponse)
async def rename_staging_file(file_id: str, request: RenameRequest):
    """重命名暂存文件"""
    try:
        new_name = request.name.strip()
        if not new_name:
            return ApiResponse(
                code=ErrorCode.BAD_REQUEST,
                message="文件名不能为空"
            )

        success = staging_service.rename_file(file_id, new_name)

        if not success:
            return ApiResponse(
                code=ErrorCode.NOT_FOUND,
                message="文件不存在或重命名失败"
            )

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message="重命名成功",
            data={"file_id": file_id, "name": new_name}
        )

    except Exception as e:
        logger.error(f"重命名暂存文件失败: {str(e)}")
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
