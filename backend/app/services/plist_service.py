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
    def preview_plist(plist_path: Path) -> Dict:
        """
        预览 PLIST 文件内容

        Args:
            plist_path: PLIST 文件路径

        Returns:
            包含条目信息的字典
        """
        try:
            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            entries = []
            for key, value in plist_data.items():
                if isinstance(value, str):
                    # 计算 base64 解码后的实际大小
                    try:
                        decoded_size = len(base64.b64decode(value))
                    except Exception:
                        decoded_size = 0

                    entries.append({
                        "key": key,
                        "data_size": len(value),
                        "decoded_size": decoded_size
                    })

            return {
                "total_entries": len(entries),
                "entries": entries
            }

        except Exception as e:
            logger.error(f"预览 PLIST 失败: {str(e)}")
            raise

    @staticmethod
    def split_plist(
        plist_path: Path,
        split_count: int,
        output_dir: Path,
        output_prefix: str = "split",
        split_mode: str = "even",
        custom_assignments: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        将 PLIST 文件拆分为多个独立的 PLIST 文件

        Args:
            plist_path: 源 PLIST 文件路径
            split_count: 拆分数量
            output_dir: 输出目录
            output_prefix: 输出文件名前缀
            split_mode: 拆分方式 - "even"（均匀分配）或 "manual"（手动分配）
            custom_assignments: 手动分配方案

        Returns:
            拆分结果列表
        """
        try:
            # 读取源 PLIST
            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            all_keys = list(plist_data.keys())
            total_entries = len(all_keys)

            # 验证拆分数量
            if split_count < 1 or split_count > total_entries:
                raise ValueError(f"拆分数量必须在 1 到 {total_entries} 之间")

            # 创建输出目录
            output_dir.mkdir(parents=True, exist_ok=True)

            # 根据拆分方式分配条目
            if split_mode == "even":
                # 均匀分配
                assignments = []
                base_count = total_entries // split_count
                remainder = total_entries % split_count

                start_idx = 0
                for i in range(split_count):
                    count = base_count + (1 if i < remainder else 0)
                    assignments.append({
                        "file_index": i + 1,
                        "keys": all_keys[start_idx:start_idx + count]
                    })
                    start_idx += count
            else:
                # 手动分配
                if not custom_assignments:
                    raise ValueError("手动分配模式需要提供 custom_assignments")
                assignments = custom_assignments

            # 执行拆分
            result_files = []
            for assignment in assignments:
                file_index = assignment["file_index"]
                keys = assignment["keys"]

                # 构建子 PLIST 数据
                sub_plist_data = {}
                for key in keys:
                    if key in plist_data:
                        sub_plist_data[key] = plist_data[key]
                    else:
                        logger.warning(f"条目不存在: {key}")

                # 生成输出文件
                output_filename = f"{output_prefix}_{file_index}.plist"
                output_path = output_dir / output_filename

                with open(output_path, 'wb') as f:
                    plistlib.dump(sub_plist_data, f, fmt=plistlib.FMT_XML)

                result_files.append({
                    "file_index": file_index,
                    "filename": output_filename,
                    "entry_count": len(sub_plist_data),
                    "keys": list(sub_plist_data.keys())
                })

                logger.info(f"拆分生成: {output_filename} ({len(sub_plist_data)} 个条目)")

            return result_files

        except Exception as e:
            logger.error(f"PLIST 拆分失败: {str(e)}")
            raise

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
