"""
音频转换服务
参考 development.md 第 4.2.3 节、PRD.md 第 2.1.2 节
"""
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from app.config import settings
from app.logger import logger
from app.models.convert import TaskInfo, TaskStatus, ConvertRequest
from app.models.response import ApiResponse, ErrorCode, ERROR_MESSAGES
from app.services.audio_service import AudioService
from app.services.file_service import FileService


class ConvertService:
    """音频转换协调服务"""

    def __init__(self):
        self.audio_service = AudioService()
        self.file_service = FileService()
        self.temp_dir = Path(settings.temp_dir)
        self.output_dir = Path(settings.output_dir)

        # 任务存储（内存中，后续可改为 Redis）
        self.tasks: Dict[str, TaskInfo] = {}

        # 并发控制
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_tasks)

        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def upload_and_validate(self, files: list) -> ApiResponse:
        """
        上传并验证文件

        Args:
            files: 上传文件列表

        Returns:
            API 响应
        """
        try:
            validated_files = await self.file_service.upload_and_validate(files)

            # 创建任务信息
            for file_info in validated_files:
                task_info = TaskInfo(
                    task_id=file_info.task_id,
                    status=TaskStatus.PENDING,
                    progress=0
                )
                self.tasks[file_info.task_id] = task_info

            return ApiResponse(
                code=ErrorCode.SUCCESS,
                message="上传成功",
                data={"files": [f.model_dump() for f in validated_files]}
            )

        except Exception as e:
            logger.error(f"上传失败: {str(e)}")
            return ApiResponse(
                code=ErrorCode.INTERNAL_ERROR,
                message=str(e)
            )

    async def start_conversion(
        self,
        task_id: str,
        request: ConvertRequest
    ) -> ApiResponse:
        """
        开始转换任务

        Args:
            task_id: 任务 ID
            request: 转换请求参数

        Returns:
            API 响应
        """
        try:
            # 检查任务是否存在
            if task_id not in self.tasks:
                return ApiResponse(
                    code=ErrorCode.NOT_FOUND,
                    message="任务不存在"
                )

            task_info = self.tasks[task_id]

            # 更新任务状态
            task_info.status = TaskStatus.PROCESSING
            task_info.progress = 0

            # 查找上传的文件
            upload_files = list(self.file_service.upload_dir.glob(f"{task_id}_*"))
            if not upload_files:
                return ApiResponse(
                    code=ErrorCode.NOT_FOUND,
                    message="文件不存在"
                )

            input_file = upload_files[0]

            # 在后台执行转换
            asyncio.create_task(
                self._execute_conversion(
                    task_id,
                    input_file,
                    request
                )
            )

            return ApiResponse(
                code=ErrorCode.SUCCESS,
                message="转换已开始",
                data={"task_id": task_id}
            )

        except Exception as e:
            logger.error(f"转换启动失败: {str(e)}")
            return ApiResponse(
                code=ErrorCode.INTERNAL_ERROR,
                message=str(e)
            )

    async def _execute_conversion(
        self,
        task_id: str,
        input_file: Path,
        request: ConvertRequest
    ):
        """
        执行实际的转换任务

        Args:
            task_id: 任务 ID
            input_file: 输入文件路径
            request: 转换请求参数
        """
        async with self.semaphore:
            task_info = self.tasks[task_id]

            try:
                # 更新进度
                task_info.progress = 10

                # 生成输出文件名
                output_filename = f"{task_id}_output.{request.target_format.lower()}"
                output_path = self.output_dir / output_filename

                # 根据输入格式和目标格式选择转换方法
                success = False
                input_format = input_file.suffix.lower()

                if input_format == '.silk':
                    # SILK 解码 → WAV/MP3
                    if request.target_format.value == 'WAV':
                        success = await self.audio_service.silk_to_wav(
                            input_file,
                            output_path,
                            request.sample_rate or 24000
                        )
                    elif request.target_format.value == 'MP3':
                        success = await self.audio_service.silk_to_mp3(
                            input_file,
                            output_path,
                            request.sample_rate or 24000
                        )
                    else:
                        task_info.status = TaskStatus.FAILED
                        task_info.error_message = f"不支持从 SILK 转换到 {request.target_format.value}"
                        logger.error(f"❌ 不支持的转换: SILK → {request.target_format.value}")
                        return

                elif input_format == '.wav':
                    # WAV 编码 → SILK
                    if request.target_format.value == 'SILK':
                        success = await self.audio_service.wav_to_silk(
                            input_file,
                            output_path,
                            request.sample_rate or 24000,
                            request.bit_rate or 24000,
                            request.frame_size or 20,
                            request.wechat_compatible
                        )
                    else:
                        task_info.status = TaskStatus.FAILED
                        task_info.error_message = f"不支持从 WAV 转换到 {request.target_format.value}"
                        logger.error(f"❌ 不支持的转换: WAV → {request.target_format.value}")
                        return

                elif input_format == '.mp3':
                    # MP3 编码 → SILK
                    if request.target_format.value == 'SILK':
                        success = await self.audio_service.mp3_to_silk(
                            input_file,
                            output_path,
                            request.sample_rate or 24000,
                            request.bit_rate or 24000,
                            request.frame_size or 20,
                            request.wechat_compatible
                        )
                    else:
                        task_info.status = TaskStatus.FAILED
                        task_info.error_message = f"不支持从 MP3 转换到 {request.target_format.value}"
                        logger.error(f"❌ 不支持的转换: MP3 → {request.target_format.value}")
                        return

                else:
                    task_info.status = TaskStatus.FAILED
                    task_info.error_message = f"不支持的输入格式: {input_format}"
                    logger.error(f"❌ 不支持的输入格式: {input_format}")
                    return

                # 更新进度
                task_info.progress = 90

                if success:
                    # 转换成功
                    task_info.status = TaskStatus.COMPLETED
                    task_info.progress = 100
                    task_info.download_url = f"/api/download/{task_id}"

                    logger.info(f"✅ 转换成功: {task_id}")

                else:
                    # 转换失败
                    task_info.status = TaskStatus.FAILED
                    task_info.error_message = "转换失败"

                    logger.error(f"❌ 转换失败: {task_id}")

            except Exception as e:
                task_info.status = TaskStatus.FAILED
                task_info.error_message = str(e)
                logger.error(f"❌ 转换异常: {task_id} - {str(e)}")

    def get_status(self, task_id: str) -> ApiResponse:
        """
        查询转换状态

        Args:
            task_id: 任务 ID

        Returns:
            API 响应
        """
        if task_id not in self.tasks:
            return ApiResponse(
                code=ErrorCode.NOT_FOUND,
                message="任务不存在"
            )

        task_info = self.tasks[task_id]

        return ApiResponse(
            code=ErrorCode.SUCCESS,
            message="查询成功",
            data=task_info.model_dump()
        )
