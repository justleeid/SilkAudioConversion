"""
文件头检查和处理工具
参考 development.md 第 4.2.4 节、PRD.md ��� 3.1 节
"""
from pathlib import Path
from fastapi import UploadFile
from app.logger import logger


class FileHeaderChecker:
    """文件头检查和处理"""

    SILK_STANDARD_HEADER = b'#!silk_v3'
    SILK_WECHAT_HEADER = b'\x02#!silk_v3'
    SILK_FOOTER = b'\xff\xff'

    def __init__(self, file_or_path):
        """
        初始化文件头检查器

        Args:
            file_or_path: UploadFile 对象或文件路径
        """
        if isinstance(file_or_path, UploadFile):
            # 读取前 10 字节用于检测
            self.data = file_or_path.file.read(10)
            file_or_path.file.seek(0)  # 重置文件指针
        else:
            with open(file_or_path, 'rb') as f:
                self.data = f.read(10)

    def is_silk(self) -> bool:
        """检查是否为 SILK 格式"""
        data_lower = self.data.lower()
        return (data_lower.startswith(self.SILK_STANDARD_HEADER) or
                data_lower.startswith(self.SILK_WECHAT_HEADER))

    def is_wechat_silk(self) -> bool:
        """检查是否为微信 SILK 格式（带 0x02 头）"""
        return self.data.lower().startswith(self.SILK_WECHAT_HEADER)

    @staticmethod
    def normalize_silk(input_path: Path, output_path: Path) -> None:
        """
        标准化 SILK 文件（移除微信头，保留标准结构）

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        """
        with open(input_path, 'rb') as f:
            data = f.read()

        # 移除微信头（大小写不敏感）
        if data[:10].lower().startswith(FileHeaderChecker.SILK_WECHAT_HEADER):
            data = data[1:]  # 移除 0x02
            logger.info(f"移除微信 SILK 文件头: {input_path}")

        # 移除结尾标记
        if data.endswith(FileHeaderChecker.SILK_FOOTER):
            data = data[:-2]
            logger.info(f"移除 SILK 文件结尾标记: {input_path}")

        with open(output_path, 'wb') as f:
            f.write(data)

        logger.info(f"SILK 文件标准化完成: {output_path}")

    @staticmethod
    def add_wechat_header(input_path: Path, output_path: Path) -> None:
        """
        添加微信文件头（用于编码后的 SILK）

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        """
        with open(input_path, 'rb') as f:
            data = f.read()

        # 移除结尾标记（如果存在）
        if data.endswith(FileHeaderChecker.SILK_FOOTER):
            data = data[:-2]

        # 添加微信头
        data = b'\x02' + data

        with open(output_path, 'wb') as f:
            f.write(data)

        logger.info(f"添加微信 SILK 文件头: {output_path}")
