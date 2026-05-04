"""
PLIST API 路由
参考 PRD.md 第 5.5 节
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.response import ApiResponse, ErrorCode, ERROR_MESSAGES
from app.services.plist_service import PlistService
from app.logger import logger
from pathlib import Path
from app.config import settings

router = APIRouter(prefix="/api/plist", tags=["plist"])

plist_service = PlistService()


class PlistMergeRequest(BaseModel):
    """PLIST 合并请求"""
    task_ids: List[str]
    output_filename: Optional[str] = "voices.plist"
    include_metadata: bool = False


class PlistExtractRequest(BaseModel):
    """PLIST 提取请求"""
    plist_file_id: str


@router.post("/merge", response_model=ApiResponse)
async def merge_silk_to_plist(request: PlistMergeRequest):
    """合并多个 SILK 文件为一个 PLIST"""
    try:
        import uuid
        upload_dir = Path(settings.upload_dir)
        output_dir = Path(settings.output_dir)

        # 查找对应的 SILK 文件
        silk_paths = []
        for task_id in request.task_ids:
            upload_matches = list(upload_dir.glob(f"{task_id}_*"))
            output_matches = list(output_dir.glob(f"{task_id}_output.*"))
            candidates = output_matches + upload_matches

            if not candidates:
                return ApiResponse(
                    code=ErrorCode.NOT_FOUND,
                    message=f"文件不存在: {task_id}"
                )

            # 只接受 SILK 文件；优先 output 目录中的转换结果
            source_file = next((f for f in candidates if f.suffix.lower() == ".silk"), None)
            if source_file is None:
                return ApiResponse(
                    code=ErrorCode.UNSUPPORTED_FORMAT,
                    message=f"文件不是 SILK 格式: {task_id}"
                )

            silk_paths.append(source_file)

        # 生成文件 ID 和输出路径（使用标准命名以便下载端点查找）
        file_id = uuid.uuid4().hex
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{file_id}_output.plist"

        # 执行合并
        success = plist_service.merge_silk_to_plist(silk_paths, output_path)

        if not success:
            return ApiResponse(
                code=ErrorCode.CONVERSION_FAILED,
                message="PLIST 合并失败"
            )

        # 添加到暂存区
        from app.services.staging_service import StagingService
        staging = StagingService()
        await staging.add_file(
            file_id=file_id,
            original_name=request.output_filename or "voices.plist",
            output_path=output_path
        )

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message="PLIST 合并成功",
            data={
                "file_id": file_id,
                "filename": request.output_filename or "voices.plist",
                "download_url": f"/api/download/{file_id}"
            }
        )

    except Exception as e:
        logger.error(f"PLIST 合并失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )


@router.post("/extract", response_model=ApiResponse)
async def extract_plist_to_silk(request: PlistExtractRequest):
    """从 PLIST 提取 SILK 文件"""
    try:
        # 先查 output_dir，再查 uploads
        output_path = Path(settings.output_dir)
        upload_path = Path(settings.upload_dir)
        plist_path = None

        files = list(output_path.glob(f"{request.plist_file_id}_*"))
        if not files:
            files = list(upload_path.glob(f"{request.plist_file_id}_*"))

        if not files:
            return ApiResponse(
                code=ErrorCode.NOT_FOUND,
                message="PLIST 文件不存在"
            )

        plist_path = files[0]

        # 输出目录
        extract_dir = Path(settings.output_dir) / f"extracted_{request.plist_file_id}"
        extract_dir.mkdir(parents=True, exist_ok=True)

        # 执行提取
        extracted = plist_service.plist_to_silk(plist_path, extract_dir)

        if not extracted:
            return ApiResponse(
                code=ErrorCode.CONVERSION_FAILED,
                message="PLIST 提取失败或无有效 SILK 数据"
            )

        import uuid
        file_ids = []
        for p in extracted:
            fid = uuid.uuid4().hex
            file_ids.append(fid)

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message=f"成功提取 {len(extracted)} 个 SILK 文件",
            data={
                "count": len(extracted),
                "output_dir": str(extract_dir),
                "files": [p.name for p in extracted]
            }
        )

    except Exception as e:
        logger.error(f"PLIST 提取失败: {str(e)}")
        return ApiResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(e)
        )
