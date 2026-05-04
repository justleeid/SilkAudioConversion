"""
文件头检查和处理
参考 development.md 第 4.2.2 节
"""
from pathlib import Path
from app.logger import logger


class FileHeaderChecker:
    """文件头检查和处理"""

    @staticmethod
    def detect_file_type(file_path: Path) -> str:
        """
        检测文件类型（通过魔数）

        Args:
            file_path: 文件路径

        Returns:
            文件类型字符串
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)

            # SILK 格式检测
            if header.startswith(b'\x02#!SILK_V3'):
                return 'silk_wechat'
            if header.startswith(b'#!SILK_V3'):
                return 'silk_standard'

            # WAV 格式检测
            if header.startswith(b'RIFF') and b'WAVE' in header:
                return 'wav'

            # MP3 格式检测
            if header.startswith(b'\xff\xfb') or header.startswith(b'ID3'):
                return 'mp3'

            # AMR 格式检测
            if header.startswith(b'#!AMR'):
                return 'amr'

            # M4A/MP4 格式检测（ftyp at offset 4-8）
            if len(header) >= 12 and header[4:8] == b'ftyp':
                return 'm4a'

            return 'unknown'

        except Exception as e:
            logger.error(f"文件检测失败: {str(e)}")
            return 'unknown'

    @staticmethod
    def normalize_silk(input_path: Path, output_path: Path) -> bool:
        """
        标准化 SILK 文件（移除微信头）

        Args:
            input_path: 输入 SILK 文件路径
            output_path: 输出 SILK 文件路径

        Returns:
            是否成功
        """
        try:
            with open(input_path, 'rb') as f:
                data = f.read()

            # 如果有微信头（0x02），移除它
            if data.startswith(b'\x02#!SILK_V3'):
                data = data[1:]
            elif not data.startswith(b'#!SILK_V3'):
                logger.warning(f"文件不是有效的 SILK 格式: {input_path}")
                return False

            with open(output_path, 'wb') as f:
                f.write(data)

            logger.debug(f"SILK 标准化完成: {output_path}")
            return True

        except Exception as e:
            logger.error(f"SILK 标准化失败: {str(e)}")
            return False

    @staticmethod
    def add_wechat_header(input_path: Path, output_path: Path) -> bool:
        """
        添加微信头到 SILK 文件（0x02）

        Args:
            input_path: 输入 SILK 文件路径
            output_path: 输出 SILK 文件路径

        Returns:
            是否成功
        """
        try:
            with open(input_path, 'rb') as f:
                data = f.read()

            # 检查是否已有头
            if data.startswith(b'\x02'):
                # 已有微信头，直接复制
                with open(output_path, 'wb') as f:
                    f.write(data)
            elif data.startswith(b'#!SILK_V3'):
                # 没有微信头，添加
                with open(output_path, 'wb') as f:
                    f.write(b'\x02' + data)
            else:
                logger.warning(f"文件不是有效的 SILK 格式: {input_path}")
                return False

            logger.debug(f"SILK 添加微信头完成: {output_path}")
            return True

        except Exception as e:
            logger.error(f"添加微信头失败: {str(e)}")
            return False
