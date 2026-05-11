"""
FastAPI 应用主入口
参考 development.md 第 8.2 节
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import convert, plist, staging, config, db_audio
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

# 注册路由
app.include_router(convert.router)
app.include_router(plist.router)
app.include_router(staging.router)
app.include_router(config.router)
app.include_router(db_audio.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Silk 音频转换器启动")
    # 启动暂存区后台清理任务
    from app.services.staging_service import StagingService
    staging_svc = StagingService()
    await staging_svc.start_cleanup_task()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Silk 音频转换器关闭")


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "status": "ok",
        "message": "Silk 音频转换器 API",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from app.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
