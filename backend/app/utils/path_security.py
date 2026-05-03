"""
路径安全工具
参考 development.md 第 6.2 节
"""
from pathlib import Path
from app.logger import logger


def get_safe_path(base_dir: Path, filename: str) -> Path:
    """
    获取安全的文件路径，防止路径遍历攻击

    Args:
        base_dir: 基础目录
        filename: 文件名

    Returns:
        安全的文件路径

    Raises:
        ValueError: 如果文件名不合法
    """
    # 1. 禁止路径遍历
    if '..' in filename or filename.startswith('/'):
        logger.error(f"检测到路径遍历攻击尝试: {filename}")
        raise ValueError("非法文件名")

    # 2. 构建安全路径
    safe_path = (base_dir / filename).resolve()

    # 3. 验证路径在允许范围内
    if not str(safe_path).startswith(str(base_dir.resolve())):
        logger.error(f"文件路径超出允许范围: {safe_path}")
        raise ValueError("文件路径超出允许范围")

    return safe_path


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的安全文件名
    """
    # 移除路径分隔符和其他危险字符
    dangerous_chars = ['/', '\\', '..', '\0']
    safe_name = filename

    for char in dangerous_chars:
        safe_name = safe_name.replace(char, '_')

    # 移除首尾空格
    safe_name = safe_name.strip()

    # 如果文件名为空，生成一个随机名称
    if not safe_name:
        import uuid
        safe_name = f"file_{uuid.uuid4().hex}"
        logger.warning(f"文件名为空，生成随机名称: {safe_name}")

    return safe_name