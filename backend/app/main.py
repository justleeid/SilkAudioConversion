"""
FastAPI 应用主入口
参考 development.md 第 8.2 节
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import convert
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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# 注册路由
app.include_router(convert.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 Silk 音频转换器启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("👋 Silk 音频转换器关闭")


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
