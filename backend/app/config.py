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

    # 数据库配置 — MySQL（音频导入）
    db_audio_host: str = "172.16.8.52"
    db_audio_port: int = 3306
    db_audio_user: str = "lan"
    db_audio_password: str = ""
    db_audio_name: str = "xiaozhi"
    db_audio_charset: str = "utf8mb4"
    db_audio_table: str = "ai_agent_chat_audio"
    db_history_table: str = "ai_agent_chat_history"

    # 数据库配置 — SQL Server（音频导入）
    db_mssql_host: str = "172.16.8.52"
    db_mssql_port: int = 1433
    db_mssql_user: str = "lan"
    db_mssql_password: str = ""
    db_mssql_name: str = "xiaozhi"
    db_mssql_schema: str = "dbo"
    db_mssql_table: str = "ai_agent_chat_audio"
    db_mssql_history_table: str = "ai_agent_chat_history"
    # ODBC 驱动名称，可在不同机器上配置为 'ODBC Driver 17 for SQL Server' 或 'ODBC Driver 18 for SQL Server'
    db_mssql_driver: str = "ODBC Driver 17 for SQL Server"

    class Config:
        # 使用绝对路径指向 .env 文件
        import os
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        case_sensitive = False


# 全局配置实例
settings = Settings()