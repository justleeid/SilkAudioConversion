"""
数据库音频导入 API 路由
参考 development.md 第 7.3.2 节、PRD.md 第 2.1.8 节
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, Query
from typing import Optional
from pydantic import BaseModel

from app.config import settings
from app.logger import logger
from app.models.response import ApiResponse, ErrorCode
from app.models.convert import TaskInfo, TaskStatus, FileInfo
from app.services.database_audio_service import get_db_service
from app.utils.path_security import sanitize_filename, get_safe_path
from app.services.file_service import detect_file_type

# 导入 convert 模块的共享服务实例
from app.api.convert import convert_service

router = APIRouter(prefix="/api/db-audio", tags=["database_audio"])

# 管理功能开关（服务器重启后自动重置为关闭）
_admin_enabled = False


class ImportRequest(BaseModel):
    audio_ids: list[str]
    source: str = "mysql"


class UpdateTitleRequest(BaseModel):
    title: str
    source: str = "mysql"


@router.get("/query", response_model=ApiResponse)
async def query_database_audio(
    date_start: str = Query(..., description="开始日期 YYYY-MM-DD"),
    date_end: str = Query(..., description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键字搜索"),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页条数"),
    source: str = Query("mysql", description="数据源: mysql / mssql")
):
    """查询数据库中的音频记录"""
    # 验证 source 参数
    if source not in ("mysql", "mssql"):
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="source 参数必须是 'mysql' 或 'mssql'")

    try:
        service = get_db_service(source)
        result = await service.query_audio_records(
            date_start, date_end, keyword, page, per_page
        )
        return ApiResponse(code=0, message="查询成功", data=result)
    except Exception as e:
        logger.error(f"查询数据库音频失败: {str(e)}")
        return ApiResponse(code=ErrorCode.INTERNAL_ERROR, message=f"数据库查询失败: {str(e)}")


@router.post("/import", response_model=ApiResponse)
async def import_database_audio(request: ImportRequest):
    """导入选定的数据库音频到转换队列"""
    if not request.audio_ids:
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="没有选择任何音频")

    # 验证 source 参数
    if request.source not in ("mysql", "mssql"):
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="source 参数必须是 'mysql' 或 'mssql'")

    try:
        db_service = get_db_service(request.source)
        records = await db_service.get_audio_records_batch(request.audio_ids)

        if not records:
            return ApiResponse(code=ErrorCode.NOT_FOUND, message="未找到所选音频数据")

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        imported_tasks = []

        for record in records:
            audio_id = record["audio_id"]
            title = record["title"]
            blob = record["blob"]

            # 检测格式
            fmt = detect_file_type(blob[:1024])
            ext_map = {
                "audio/wav": "wav",
                "audio/mpeg": "mp3",
                "audio/silk": "silk",
                "audio/amr": "amr",
                "audio/mp4": "m4a",
            }
            ext = ext_map.get(fmt, "wav")

            # 生成 task_id 和文件名（去除标题末尾符号）
            task_id = uuid.uuid4().hex
            safe_title = sanitize_filename(title).rstrip(',.!?;:，。！？；：、')
            if not safe_title.strip():
                safe_title = f"audio_{audio_id[:8]}"
            filename = f"[DB] {safe_title}.{ext}"

            # 保存到 uploads 目录
            file_path = get_safe_path(upload_dir, f"{task_id}_{filename}")
            with open(file_path, "wb") as f:
                f.write(blob)

            # 注册到转换服务
            task_info = TaskInfo(
                task_id=task_id,
                status=TaskStatus.PENDING,
                progress=0
            )
            convert_service.tasks[task_id] = task_info

            # 构建返回信息
            file_info = FileInfo(
                task_id=task_id,
                filename=filename,
                size=record["size"],
                format=ext.upper()
            )
            imported_tasks.append(file_info.model_dump())

            logger.info(f"数据库音频导入: {audio_id} -> task_id={task_id}, filename={filename}")

        return ApiResponse(
            code=0,
            message=f"成功导入 {len(imported_tasks)} 个文件",
            data={
                "imported_count": len(imported_tasks),
                "files": imported_tasks
            }
        )

    except Exception as e:
        logger.error(f"导入数据库音频失败: {str(e)}")
        return ApiResponse(code=ErrorCode.INTERNAL_ERROR, message=f"导入失败: {str(e)}")


@router.get("/preview/{audio_id}")
async def preview_database_audio(
    audio_id: str,
    source: str = Query("mysql", description="数据源: mysql / mssql")
):
    """获取数据库音频的预览（返回音频流供浏览器播放）"""
    from fastapi.responses import Response

    # 验证 source 参数
    if source not in ("mysql", "mssql"):
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="source 参数必须是 'mysql' 或 'mssql'")

    try:
        db_service = get_db_service(source)
        blob = await db_service.get_audio_blob(audio_id)

        fmt = detect_file_type(blob[:1024])
        content_type_map = {
            "audio/wav": "audio/wav",
            "audio/mpeg": "audio/mpeg",
            "audio/silk": "audio/ogg",
            "audio/amr": "audio/amr",
            "audio/mp4": "audio/mp4",
        }
        content_type = content_type_map.get(fmt, "audio/wav")

        return Response(content=blob, media_type=content_type)

    except ValueError as e:
        return ApiResponse(code=ErrorCode.NOT_FOUND, message=str(e))
    except Exception as e:
        logger.error(f"预览音频失败: {str(e)}")
        return ApiResponse(code=ErrorCode.INTERNAL_ERROR, message=f"预览失败: {str(e)}")


# -- 管理功能开关 --

@router.post("/admin/enable", response_model=ApiResponse)
async def enable_admin():
    """启用数据库管理功能（删除 / 修改标题），前端检测到此状态后显示操作按钮"""
    global _admin_enabled
    _admin_enabled = True
    logger.info("数据库管理功能已启用")
    return ApiResponse(code=0, message="管理功能已启用，前端刷新后生效")


@router.get("/admin/status", response_model=ApiResponse)
async def admin_status():
    """查询管理功能是否已启用"""
    return ApiResponse(code=0, message="查询成功", data={"admin_enabled": _admin_enabled})


# -- 记录增删改 --

@router.delete("/record/{audio_id}", response_model=ApiResponse)
async def delete_audio_record(
    audio_id: str,
    source: str = Query("mysql", description="数据源: mysql / mssql")
):
    """删除数据库中的音频记录及关联的聊天记录"""
    if source not in ("mysql", "mssql"):
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="source 参数必须是 'mysql' 或 'mssql'")

    try:
        db_service = get_db_service(source)
        affected = await db_service.delete_audio_record(audio_id)
        if affected == 0:
            return ApiResponse(code=ErrorCode.NOT_FOUND, message="未找到对应记录")
        return ApiResponse(code=0, message=f"已删除音频记录及关联数据", data={"affected": affected})
    except Exception as e:
        logger.error(f"删除音频记录失败: {str(e)}")
        return ApiResponse(code=ErrorCode.INTERNAL_ERROR, message=f"删除失败: {str(e)}")


@router.put("/record/{audio_id}/title", response_model=ApiResponse)
async def update_audio_title(
    audio_id: str,
    request: UpdateTitleRequest
):
    """修改音频记录的标题（history.content）"""
    if request.source not in ("mysql", "mssql"):
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="source 参数必须是 'mysql' 或 'mssql'")

    if not request.title or not request.title.strip():
        return ApiResponse(code=ErrorCode.BAD_REQUEST, message="标题不能为空")

    try:
        db_service = get_db_service(request.source)
        affected = await db_service.update_audio_title(audio_id, request.title.strip())
        if affected == 0:
            return ApiResponse(code=ErrorCode.NOT_FOUND, message="未找到对应记录")
        return ApiResponse(code=0, message="标题已更新", data={"affected": affected})
    except Exception as e:
        logger.error(f"修改音频标题失败: {str(e)}")
        return ApiResponse(code=ErrorCode.INTERNAL_ERROR, message=f"修改失败: {str(e)}")
