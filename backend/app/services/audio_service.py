"""
音频处理服务
参考 development.md 第 4.2.5 节、PRD.md 第 3.2 节
"""
import subprocess
import asyncio
from pathlib import Path
from typing import Optional
from app.config import settings
from app.logger import logger
from app.utils.file_header import FileHeaderChecker


class AudioService:
    """音频编解码服务"""

    def __init__(self):
        self.decoder_path = Path(settings.silk_decoder_bin)
        self.encoder_path = Path(settings.silk_encoder_bin)
        self.temp_dir = Path(settings.temp_dir)
        self.output_dir = Path(settings.output_dir)

        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def silk_to_wav(
        self,
        silk_path: Path,
        output_path: Path,
        sample_rate: int = 24000
    ) -> bool:
        """
        SILK 解码为 WAV

        Args:
            silk_path: SILK 文件路径
            output_path: 输出 WAV 文件路径
            sample_rate: 采样率

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 SILK 解码: {silk_path}")

            # 1. 标准化 SILK 文件（移除微信头）
            normalized_silk = self.temp_dir / f"normalized_{silk_path.name}"
            FileHeaderChecker.normalize_silk(silk_path, normalized_silk)

            # 2. SILK 转 PCM
            pcm_path = self.temp_dir / f"{silk_path.stem}.pcm"
            cmd_decode = [
                str(self.decoder_path),
                str(normalized_silk),
                str(pcm_path)
            ]

            logger.debug(f"执行解码命令: {' '.join(cmd_decode)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_decode,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"SILK 解码失败: {stderr.decode()}")
                return False

            logger.info(f"SILK 转 PCM 成功: {pcm_path}")

            # 3. PCM 转 WAV（使用 ffmpeg）
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-f', 's16le',
                '-ar', str(sample_rate),
                '-ac', '1',
                '-i', str(pcm_path),
                str(output_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"PCM 转 WAV 失败: {stderr.decode()}")
                return False

            logger.info(f"✅ SILK 转 WAV 成功: {output_path}")

            # 4. 清理临时文件
            normalized_silk.unlink(missing_ok=True)
            pcm_path.unlink(missing_ok=True)

            return True

        except Exception as e:
            logger.error(f"❌ SILK 转 WAV 失败: {str(e)}")
            return False

    async def silk_to_mp3(
        self,
        silk_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 128000
    ) -> bool:
        """
        SILK 解码为 MP3

        Args:
            silk_path: SILK 文件路径
            output_path: 输出 MP3 文件路径
            sample_rate: 采样率
            bit_rate: MP3 比特率

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 SILK 转 MP3: {silk_path}")

            # 1. 先转为 WAV
            wav_path = self.temp_dir / f"{silk_path.stem}.wav"
            success = await self.silk_to_wav(silk_path, wav_path, sample_rate)

            if not success:
                return False

            # 2. WAV 转 MP3
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(wav_path),
                '-codec:a', 'libmp3lame',
                '-b:a', f'{bit_rate // 1000}k',
                str(output_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"WAV 转 MP3 失败: {stderr.decode()}")
                return False

            logger.info(f"✅ SILK 转 MP3 成功: {output_path}")

            # 3. 清理临时文件
            wav_path.unlink(missing_ok=True)

            return True

        except Exception as e:
            logger.error(f"❌ SILK 转 MP3 失败: {str(e)}")
            return False

    async def wav_to_silk(
        self,
        wav_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 24000,
        frame_size: int = 20,
        wechat_compatible: bool = True
    ) -> bool:
        """
        WAV 编码为 SILK

        Args:
            wav_path: WAV ���件路径
            output_path: 输出 SILK 文件路径
            sample_rate: 采样率
            bit_rate: 比特率
            frame_size: 帧大小
            wechat_compatible: 是否输出微信兼容格式

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 WAV 编码为 SILK: {wav_path}")

            # 1. WAV 转 PCM（使用 ffmpeg）
            pcm_path = self.temp_dir / f"{wav_path.stem}.pcm"
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(wav_path),
                '-f', 's16le',
                '-ar', str(sample_rate),
                '-ac', '1',
                str(pcm_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"WAV 转 PCM 失败: {stderr.decode()}")
                return False

            logger.info(f"WAV 转 PCM 成功: {pcm_path}")

            # 2. PCM 编码为 SILK
            temp_silk = self.temp_dir / f"{wav_path.stem}_temp.silk"
            cmd_encode = [
                str(self.encoder_path),
                str(pcm_path),
                str(temp_silk),
                '-Fs_API', str(sample_rate),
                '-rate', str(bit_rate),
                '-packetlength', str(frame_size)
            ]

            # 如果需要微信兼容，添加 -tencent 参数（encoder 会自动添加 0x02 头）
            if wechat_compatible:
                cmd_encode.append('-tencent')

            logger.debug(f"执行编码命令: {' '.join(cmd_encode)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_encode,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"PCM 编码为 SILK 失败: {stderr.decode()}")
                return False

            logger.info(f"PCM 编码为 SILK ���功: {temp_silk}")

            # 3. 根据需求处理文件
            import shutil
            if wechat_compatible:
                # 微信兼容格式：encoder 已经添加了 0x02 头，直接移动
                shutil.move(str(temp_silk), str(output_path))
                logger.info(f"✅ WAV 转 SILK 成功（微信格式）: {output_path}")
            else:
                # 标准格式：移除��能存在的微信头
                with open(temp_silk, 'rb') as f:
                    data = f.read()

                # 如果有微信头，移除它
                if data.startswith(b'\x02#!SILK_V3'):
                    data = data[1:]  # 移除 0x02

                with open(output_path, 'wb') as f:
                    f.write(data)

                temp_silk.unlink(missing_ok=True)
                logger.info(f"✅ WAV 转 SILK 成功（标准格式）: {output_path}")

            # 4. 清理临时文件
            pcm_path.unlink(missing_ok=True)

            return True

        except Exception as e:
            logger.error(f"❌ WAV 转 SILK 失败: {str(e)}")
            return False

    async def mp3_to_silk(
        self,
        mp3_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 24000,
        frame_size: int = 20,
        wechat_compatible: bool = True
    ) -> bool:
        """
        MP3 编码为 SILK

        Args:
            mp3_path: MP3 文件路径
            output_path: 输出 SILK 文件路径
            sample_rate: 采样率
            bit_rate: 比特率
            frame_size: 帧大小
            wechat_compatible: 是否输出微信兼容格式

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 MP3 编码为 SILK: {mp3_path}")

            # 1. MP3 转 WAV
            wav_path = self.temp_dir / f"{mp3_path.stem}.wav"
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(mp3_path),
                str(wav_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"MP3 转 WAV 失败: {stderr.decode()}")
                return False

            logger.info(f"MP3 转 WAV 成功: {wav_path}")

            # 2. WAV 转 SILK
            success = await self.wav_to_silk(
                wav_path,
                output_path,
                sample_rate,
                bit_rate,
                frame_size,
                wechat_compatible
            )

            # 3. 清理临时文件
            wav_path.unlink(missing_ok=True)

            if success:
                logger.info(f"✅ MP3 转 SILK 成功: {output_path}")
            else:
                logger.error(f"❌ MP3 转 SILK 失败")

            return success

        except Exception as e:
            logger.error(f"❌ MP3 转 SILK 失败: {str(e)}")
            return False

    async def amr_to_wav(
        self,
        amr_path: Path,
        output_path: Path,
        sample_rate: int = 24000
    ) -> bool:
        """
        AMR 转换为 WAV

        Args:
            amr_path: AMR 文件路径
            output_path: 输出 WAV 文件路径
            sample_rate: 采样率

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 AMR 转 WAV: {amr_path}")

            # 使用 ffmpeg 将 AMR 转为 WAV
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(amr_path),
                '-ar', str(sample_rate),
                '-ac', '1',
                str(output_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"AMR 转 WAV 失败: {stderr.decode()}")
                return False

            logger.info(f"✅ AMR 转 WAV 成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ AMR 转 WAV 失败: {str(e)}")
            return False

    async def amr_to_mp3(
        self,
        amr_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 128000
    ) -> bool:
        """
        AMR 转换为 MP3

        Args:
            amr_path: AMR 文件路径
            output_path: 输出 MP3 文件路径
            sample_rate: 采样率
            bit_rate: MP3 比特率

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 AMR 转 MP3: {amr_path}")

            # 1. 先转 WAV
            wav_path = self.temp_dir / f"{amr_path.stem}.wav"
            success = await self.amr_to_wav(amr_path, wav_path, sample_rate)

            if not success:
                return False

            # 2. WAV 转 MP3
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(wav_path),
                '-codec:a', 'libmp3lame',
                '-b:a', f'{bit_rate // 1000}k',
                str(output_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"WAV 转 MP3 失败: {stderr.decode()}")
                return False

            logger.info(f"✅ AMR 转 MP3 成功: {output_path}")

            # 3. 清理临时文件
            wav_path.unlink(missing_ok=True)

            return True

        except Exception as e:
            logger.error(f"❌ AMR 转 MP3 失败: {str(e)}")
            return False

    async def amr_to_silk(
        self,
        amr_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 24000,
        frame_size: int = 20,
        wechat_compatible: bool = True
    ) -> bool:
        """
        AMR 转换为 SILK

        Args:
            amr_path: AMR 文件路径
            output_path: 输出 SILK 文件路径
            sample_rate: 采样率
            bit_rate: 比特率
            frame_size: 帧大小
            wechat_compatible: 是否输出微信兼容格式

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 AMR 转 SILK: {amr_path}")

            # 1. 先转 WAV
            wav_path = self.temp_dir / f"{amr_path.stem}.wav"
            success = await self.amr_to_wav(amr_path, wav_path, sample_rate)

            if not success:
                return False

            # 2. WAV 转 SILK
            success = await self.wav_to_silk(
                wav_path,
                output_path,
                sample_rate,
                bit_rate,
                frame_size,
                wechat_compatible
            )

            # 3. 清理临时文件
            wav_path.unlink(missing_ok=True)

            if success:
                logger.info(f"✅ AMR 转 SILK 成功: {output_path}")
            else:
                logger.error(f"❌ AMR 转 SILK 失败")

            return success

        except Exception as e:
            logger.error(f"❌ AMR 转 SILK 失败: {str(e)}")
            return False

    async def m4a_to_wav(
        self,
        m4a_path: Path,
        output_path: Path,
        sample_rate: int = 24000
    ) -> bool:
        """
        M4A 转换为 WAV

        Args:
            m4a_path: M4A 文件路径
            output_path: 输出 WAV 文件路径
            sample_rate: 采样率

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 M4A 转 WAV: {m4a_path}")

            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(m4a_path),
                '-ar', str(sample_rate),
                '-ac', '1',
                str(output_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"M4A 转 WAV 失败: {stderr.decode()}")
                return False

            logger.info(f"✅ M4A 转 WAV 成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ M4A 转 WAV 失败: {str(e)}")
            return False

    async def m4a_to_mp3(
        self,
        m4a_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 128000
    ) -> bool:
        """
        M4A 转换为 MP3

        Args:
            m4a_path: M4A 文件路径
            output_path: 输出 MP3 文件路径
            sample_rate: 采样率
            bit_rate: MP3 比特率

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 M4A 转 MP3: {m4a_path}")

            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', str(m4a_path),
                '-ar', str(sample_rate),
                '-ac', '1',
                '-codec:a', 'libmp3lame',
                '-b:a', f'{bit_rate // 1000}k',
                str(output_path)
            ]

            logger.debug(f"执行 ffmpeg 命令: {' '.join(cmd_ffmpeg)}")
            process = await asyncio.create_subprocess_exec(
                *cmd_ffmpeg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"M4A 转 MP3 失败: {stderr.decode()}")
                return False

            logger.info(f"✅ M4A 转 MP3 成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ M4A 转 MP3 失败: {str(e)}")
            return False

    async def m4a_to_silk(
        self,
        m4a_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        bit_rate: int = 24000,
        frame_size: int = 20,
        wechat_compatible: bool = True
    ) -> bool:
        """
        M4A 转换为 SILK

        Args:
            m4a_path: M4A 文件路径
            output_path: 输出 SILK 文件路径
            sample_rate: 采样率
            bit_rate: 比特率
            frame_size: 帧大小
            wechat_compatible: 是否输出微信兼容格式

        Returns:
            是否成功
        """
        try:
            logger.info(f"开始 M4A 转 SILK: {m4a_path}")

            wav_path = self.temp_dir / f"{m4a_path.stem}.wav"
            success = await self.m4a_to_wav(m4a_path, wav_path, sample_rate)

            if not success:
                return False

            success = await self.wav_to_silk(
                wav_path,
                output_path,
                sample_rate,
                bit_rate,
                frame_size,
                wechat_compatible
            )

            wav_path.unlink(missing_ok=True)

            if success:
                logger.info(f"✅ M4A 转 SILK 成功: {output_path}")
            else:
                logger.error("❌ M4A 转 SILK 失败")

            return success

        except Exception as e:
            logger.error(f"❌ M4A 转 SILK 失败: {str(e)}")
            return False
