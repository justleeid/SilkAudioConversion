"""
应用配置模块
参考 development.md 第 7.2 节
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # 文件上传配置
    upload_dir: str = "./uploads"
    temp_dir: str = "./temp"
    output_dir: str = "./output"
    max_file_size: int = 52428800  # 50 MB
    max_file_count: int = 50

    # SILK 工具路径
    silk_decoder_bin: str = "./tools/silk-v3-decoder/silk/decoder"
    silk_encoder_bin: str = "./tools/silk-v3-decoder/silk/encoder"

    # 任务队列配置
    max_concurrent_tasks: int = 5
    task_timeout: int = 3600

    # 暂存区配置
    cache_expire_hours: int = 48
    cache_cleanup_interval: int = 3600

    class Config:
        # 使用绝对路径指向 .env 文件
        import os
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        case_sensitive = False


# 全局配置实例
settings = Settings()
