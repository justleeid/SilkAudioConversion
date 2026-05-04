"""
PLIST 转换服务
参考 PRD.md 第 2.1.4 节、第 3.4 节
"""
import base64
import plistlib
from pathlib import Path
from typing import List, Dict, Optional
from app.logger import logger


class PlistService:
    """PLIST 格式转换服务"""

    @staticmethod
    def silk_to_plist(
        silk_path: Path,
        output_path: Path,
        key_name: Optional[str] = None
    ) -> bool:
        """
        单个 SILK 文件转换为 PLIST 格式

        Args:
            silk_path: SILK 文件路径
            output_path: 输出 PLIST 文件路径
            key_name: PLIST 中的 key 名称，默认使用文件名

        Returns:
            是否成功
        """
        try:
            with open(silk_path, 'rb') as f:
                silk_data = f.read()

            encoded = base64.b64encode(silk_data).decode('ascii')
            key = key_name or silk_path.name

            plist_data = {key: encoded}

            with open(output_path, 'wb') as f:
                plistlib.dump(plist_data, f, fmt=plistlib.FMT_XML)

            logger.info(f"SILK 转 PLIST 成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"SILK 转 PLIST 失败: {str(e)}")
            return False

    @staticmethod
    def merge_silk_to_plist(
        silk_paths: List[Path],
        output_path: Path,
        key_names: Optional[List[str]] = None
    ) -> bool:
        """
        多个 SILK 文件合并为一个 PLIST 文件

        Args:
            silk_paths: SILK 文件路径列表
            output_path: 输出 PLIST 文件路径
            key_names: 自定义 key 名称列表，默认使用各文件名

        Returns:
            是否成功
        """
        try:
            plist_data: Dict[str, str] = {}

            for i, silk_path in enumerate(silk_paths):
                with open(silk_path, 'rb') as f:
                    silk_data = f.read()

                encoded = base64.b64encode(silk_data).decode('ascii')

                if key_names and i < len(key_names):
                    key = key_names[i]
                else:
                    key = silk_path.name

                plist_data[key] = encoded

            with open(output_path, 'wb') as f:
                plistlib.dump(plist_data, f, fmt=plistlib.FMT_XML)

            logger.info(f"合并 {len(silk_paths)} 个 SILK 为 PLIST: {output_path}")
            return True

        except Exception as e:
            logger.error(f"合并 SILK 为 PLIST 失败: {str(e)}")
            return False

    @staticmethod
    def plist_to_silk(
        plist_path: Path,
        output_dir: Path
    ) -> List[Path]:
        """
        从 PLIST 文件中提取 SILK 文件

        Args:
            plist_path: PLIST 文件路径
            output_dir: 输出目录

        Returns:
            提取的 SILK 文件路径列表
        """
        try:
            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            output_dir.mkdir(parents=True, exist_ok=True)
            extracted = []

            for key, value in plist_data.items():
                if not isinstance(value, str):
                    logger.warning(f"跳过非字符串值: {key}")
                    continue

                try:
                    silk_data = base64.b64decode(value)
                except Exception:
                    logger.warning(f"跳过无效 base64: {key}")
                    continue

                silk_path = output_dir / key
                with open(silk_path, 'wb') as f:
                    f.write(silk_data)

                extracted.append(silk_path)

            logger.info(f"从 PLIST 提取 {len(extracted)} 个 SILK 文件到: {output_dir}")
            return extracted

        except Exception as e:
            logger.error(f"PLIST 转 SILK 失败: {str(e)}")
            return []
