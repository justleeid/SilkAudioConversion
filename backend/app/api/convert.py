"""
转换 API 路由
参考 development.md 第 4.3.1 节、PRD.md 第 5.1 节
"""
import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from app.config import settings
from app.logger import logger
from app.models.convert import ConvertRequest
from app.models.response import ApiResponse, ErrorCode
from app.services.convert_service import ConvertService
from app.services.staging_service import StagingService

router = APIRouter(prefix="/api", tags=["convert"])

convert_service = ConvertService()
staging_service = StagingService()


@router.post("/upload", response_model=ApiResponse)
async def upload_files(files: list[UploadFile] = File(...)):
    """
    上传文件

    Args:
        files: 文件列表

    Returns:
        API 响应
    """
    logger.info(f"接收到 {len(files)} 个文件的上传请求")
    return await convert_service.upload_and_validate(files)


@router.post("/convert/{task_id}", response_model=ApiResponse)
async def start_conversion(task_id: str, request: ConvertRequest):
    """
    开始转换

    Args:
        task_id: 任务 ID
        request: 转换请求

    Returns:
        API 响应
    """
    logger.info(f"开始转换任务: {task_id}")
    return await convert_service.start_conversion(task_id, request)


@router.get("/status/{task_id}", response_model=ApiResponse)
def query_status(task_id: str):
    """
    查询转换状态

    Args:
        task_id: 任务 ID

    Returns:
        API 响应
    """
    return convert_service.get_status(task_id)


@router.get("/download/{task_id}")
async def download_file(task_id: str):
    """
    下载转换结果

    Args:
        task_id: 任务 ID

    Returns:
        文件流
    """
    try:
        # 从暂存区获取文件信息
        staging_file = staging_service.get_file(task_id)
        if not staging_file:
            return ApiResponse(
                code=ErrorCode.NOT_FOUND,
                message="文件不存在"
            )

        # 查找实际文件
        output_dir = os.path.join(settings.output_dir)
        for file_path in os.listdir(output_dir):
            if file_path.startswith(f"{task_id}_output"):
                full_path = os.path.join(output_dir, file_path)
                # 使用友好的输出名称
                filename = staging_file.output_name

                logger.info(f"下载文件: {filename}")

                return FileResponse(
                    path=full_path,
                    filename=filename,
                    media_type='application/octet-stream'
                )

        return ApiResponse(
            code=ErrorCode.NOT_FOUND,
            message="文件不存在"
        )

    except Exception as e:
        logger.error(f"下载失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )
