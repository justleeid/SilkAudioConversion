"""
转换 API 路由
参考 development.md 第 4.2.1 节、PRD.md 第 5 节
"""
from fastapi import APIRouter, UploadFile, File
from typing import List
from app.models.convert import ConvertRequest
from app.models.response import ApiResponse
from app.services.convert_service import ConvertService

router = APIRouter(prefix="/api", tags=["convert"])

# 创建转换服务实例
convert_service = ConvertService()


@router.post("/upload", response_model=ApiResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    上传音频文件

    Args:
        files: 上传文件列表���

    Returns:
        上传结果
    """
    return await convert_service.upload_and_validate(files)


@router.post("/convert/{task_id}", response_model=ApiResponse)
async def convert(task_id: str, request: ConvertRequest):
    """
    执行转换操作

    Args:
        task_id: 任务 ID
        request: 转换请求参数

    Returns:
        转换结果
    """
    return await convert_service.start_conversion(task_id, request)


@router.get("/convert/{task_id}/status", response_model=ApiResponse)
async def query_status(task_id: str):
    """
    查询转换状态

    Args:
        task_id: 任务 ID

    Returns:
        任务状态信息
    """
    return convert_service.get_status(task_id)


@router.get("/download/{task_id}")
async def download(task_id: str):
    """
    下载转换后的文件

    Args:
        task_id: 任务 ID

    Returns:
        文件下载响应
    """
    from fastapi.responses import FileResponse
    from pathlib import Path
    from app.config import settings
    from app.models.response import ApiResponse, ErrorCode
    from app.services.staging_service import StagingService

    # 查找输出文件
    output_dir = Path(settings.output_dir)
    files = list(output_dir.glob(f"{task_id}_output.*"))

    if not files:
        return ApiResponse(
            code=ErrorCode.NOT_FOUND,
            message="文件不存在或已过期"
        )

    file_path = files[0]
    
    # 从暂存区获取原始文件名
    staging = StagingService()
    staging_file = staging.get_file(task_id)
    
    if staging_file:
        # 使用原始文件名去掉扩展名，加上目标格式后缀
        import os
        original_base = os.path.splitext(staging_file.original_name)[0]
        target_ext = file_path.suffix
        # 构建用户友好的文件名
        download_filename = f"{original_base}{target_ext}"
    else:
        # 降级方案：使用原始输出文件名
        download_filename = file_path.name

    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type='application/octet-stream'
    )
