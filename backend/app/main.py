"""
FastAPI 应用主入口
参考 development.md 第 8.2 节
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import convert, plist, staging, config, db_audio
from app.services.staging_service import StagingService
from app.logger import logger

# 创建 FastAPI 应用
app = FastAPI(
    title="Silk 音频转换器",
    description="SILK 音频格式转换 Web API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

@app.get("/health")
async def health_check():
    """健康检查端点（必须在 mount 前端静态目录之前注册，避免被静态路由拦截）"""
    return {"status": "healthy"}


# 注册路由
app.include_router(convert.router)
app.include_router(plist.router)
app.include_router(staging.router)
app.include_router(config.router)
app.include_router(db_audio.router)

# 托管前端构建产物（单端口部署：前端页面与 /api 同源）
# mount 必须在 API 路由之后，保证 /api/* 优先命中后端接口
_FRONTEND_DIST = Path(__file__).resolve().parents[2] / 'frontend-v2' / 'dist'
if _FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_FRONTEND_DIST, html=True), name="frontend")
    logger.info(f"前端静态资源已托管: {_FRONTEND_DIST}")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Silk 音频转换器启动")
    # 启动暂存区后台清理任务
    staging_svc = StagingService()
    await staging_svc.start_cleanup_task()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Silk 音频转换器关闭")


if __name__ == "__main__":
    import uvicorn
    from app.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
