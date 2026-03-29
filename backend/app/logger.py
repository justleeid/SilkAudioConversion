"""
日志配置模块
参考 development.md 第 4.3 节
"""
import sys
from loguru import logger
from app.config import settings

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level=settings.log_level,
    colorize=True
)

# 添加文件输出
logger.add(
    settings.log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.log_level,
    rotation="500 MB",
    retention="7 days",
    compression="zip"
)

# 导出配置好的 logger
__all__ = ["logger"]
