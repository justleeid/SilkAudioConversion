# Silk 音频格式转换 Web 应用 - 技术规范文档

**版本**: v1.1  
**创建日期**: 2026-03-19  
**最后更新**: 2026-03-19  
**状态**: ✅ 可用于开发指导

---

## 1. 文档目的

本文档旨在为开发团队提供明确的技术规范和实现细节，确保：

- ✅ 使用成熟框架和开源组件，避免重复造轮子
- ✅ 代码风格统一，便于维护
- ✅ 所有服务本地部署，不依赖云服务
- ✅ 防止开发过程中的随意性和技术债务

**本文档优先级高于 PRD 文档，开发时必须严格遵守。**

---

## 2. 技术栈选型（已确认）

### 2.1 前端技术栈

| 组件 | 技术选型 | 版本 | 理由 |
|------|----------|------|------|
| 框架 | Vue 3 | 3.4.x | 成熟稳定，Composition API |
| 构建工具 | Vite | 5.x | 快速开发，热更新 |
| UI 组件库 | Element Plus | 2.4.x | 成熟中文组件库，移动端支持 |
| 语言 | TypeScript | 5.x | 类型安全，减少运行时错误 |
| 状态管理 | Pinia | 2.x | Vue 3 官方推荐，轻量 |
| HTTP 客户端 | Axios | 1.x | 成熟稳定，拦截器支持 |
| 文件上传 | Element Plus Upload | 2.4.x | 与 UI 组件库一致，支持拖拽与自定义上传流程 |
| 代码规范 | ESLint + Prettier | 最新 | 统一代码风格 |

### 2.2 后端技术栈

| 组件 | 技术选型 | 版本 | 理由 |
|------|----------|------|------|
| 框架 | FastAPI | 0.109.x | 高性能，自动文档，类型提示 |
| ASGI 服务器 | Uvicorn | 0.27.x | 轻量高效 |
| 虚拟环境 | Conda/venv | 最新 | 依赖隔离 |
| 文件处理 | python-multipart | 0.0.6 | FastAPI 官方推荐 |
| 文件验证 | python-magic | 0.4.27 | 文件类型魔数验证 |
| 任务队列 | asyncio + asyncio.Semaphore | 内置 | 轻量，无需额外服务 |
| 日志 | loguru | 0.7.x | 简洁易用，轮转支持 |
| 配置管理 | pydantic-settings | 2.x | 类型安全配置 |
| 安全 | python-jose | 3.x | 如需扩展认证 |

### 2.3 音频处理引擎

| 组件 | 技术选型 | 版本 | 理由 |
|------|----------|------|------|
| SILK 解码 | silk-v3-decoder | 最新 | 社区维护，MIT 协议 |
| SILK 编码 | silk-v3-encoder | 最新 | 配套编码器 |
| 音频转换 | ffmpeg | 6.x | 行业标准，格式支持全 |
| PLIST 处理 | defusedxml + plistlib | 内置 | Python 标准库，安全 |

### 2.4 部署技术栈

| 组件 | 技术选型 | 版本 | 理由 |
|------|----------|------|------|
| 容器化 | Docker | 24.x | 环境一致性 |
| 编排 | Docker Compose | 2.x | 多服务管理 |
| 反向代理 | Nginx | 1.25.x | 高性能，配置简单 |
| 进程管理 | Supervisor | 4.x | 非 Docker 部署备选 |

---

## 3. 项目结构规范

### 3.1 整体目录结构

```
silk_encode/
├── frontend/                  # Vue 3 前端应用
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # HTTP API 调用
│   │   ├── types/             # TypeScript 类型定义
│   │   └── main.ts
│   ├── vite.config.ts
│   └── package.json
├── backend/                   # FastAPI 后端应用
│   ├── app/
│   │   ├── main.py
│   │   ├── api/               # 路由定义
│   │   ├── services/          # 业务逻辑
│   │   ├── models/            # 数据模型
│   │   ├── config.py
│   │   └── logger.py
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
├── PRDs/                      # 产品与设计文档
│   ├── PRD.md
│   ├── development.md
│   └── ui.md
└── README.md
```

### 3.2 Git Submodule 配置

```bash
git submodule add https://github.com/kn007/silk-v3-decoder tools/silk-v3-decoder
git submodule add https://github.com/tafayor/silk-codec tools/silk-v3-encoder
```

---

## 4. 编码规范

### 4.1 前端编码规范

#### 4.1.1 文件结构

```typescript
// 组件文件结构 (src/components/MyComponent.vue)
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 导入
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'

// 类型定义
interface Props {
  title: string
}

// 定义属性
const props = withDefaults(defineProps<Props>(), {
  title: '默认标题'
})

// 状态与计算属性
const state = ref<string>('')

// 方法
const handleClick = () => {
  // 实现逻辑
}
</script>

<style scoped>
/* 样式 */
</style>
```

#### 4.1.2 API 调用规范

```typescript
// src/api/convert.ts
import axios from 'axios'
import type { ApiResponse } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
})

// 统一响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error)
)

export const convertApi = {
  upload: (files: File[]) => 
    api.post<FormData, ApiResponse>('/api/upload', formData),
    
  convert: (taskId: string, params: ConvertParams) =>
    api.post<ConvertParams, ApiResponse>(`/api/convert/${taskId}`, params),
    
  queryStatus: (taskId: string) =>
    api.get<never, ApiResponse>(`/api/convert/${taskId}/status`)
}
```

#### 4.1.3 类型定义规范

```typescript
// src/types/index.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

export interface ConvertParams {
  targetFormat: 'WAV' | 'MP3' | 'SILK' | 'PLIST'
  wechatCompatible: boolean
  sampleRate?: number
  bitRate?: number
  frameSize?: number
}

export interface UploadProgress {
  taskId: string
  progress: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  errorMessage?: string
}
```

### 4.2 后端编码规范

#### 4.2.1 FastAPI 路由规范

```python
# app/api/convert.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from app.models import ConvertRequest, ApiResponse
from app.services import ConvertService

router = APIRouter(prefix="/api/convert", tags=["convert"])

@router.post("/upload", response_model=ApiResponse)
async def upload_files(files: list[UploadFile] = File(...)):
    """上传音频文件"""
    service = ConvertService()
    return await service.upload_and_validate(files)

@router.post("/{task_id}", response_model=ApiResponse)
async def convert(task_id: str, request: ConvertRequest):
    """执行转换操作"""
    service = ConvertService()
    return await service.start_conversion(task_id, request)

@router.get("/{task_id}/status", response_model=ApiResponse)
async def query_status(task_id: str):
    """查询转换状态"""
    service = ConvertService()
    return await service.get_status(task_id)
```

#### 4.2.2 统一响应格式

```python
# app/models/response.py
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int          # 0 成功，其他值为错误码
    message: str       # 成功或错误消息
    data: Optional[T] = None

# 错误码定义
ERROR_CODES = {
    400: "请求参数错误",
    401: "未授权",
    403: "禁止访问",
    404: "资源不存在",
    413: "文件过大",
    500: "服务器错误",
    1001: "无效的 SILK 文件头",
    1002: "不支持的文件格式",
    1003: "转换失败",
}

# 成功响应示例
success_response = ApiResponse(
    code=0,
    message="操作成功",
    data={"task_id": "abc123"}
)
```

#### 4.2.3 服务层规范

```python
# app/services/convert_service.py
from pathlib import Path
from app.models import ConvertRequest, FileInfo
from app.utils import FileHeaderChecker, get_safe_path
from loguru import logger

class ConvertService:
    """音频转换服务"""
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
    
    async def upload_and_validate(self, files: list[UploadFile]) -> ApiResponse:
        """上传并验证文件"""
        try:
            validated_files = []
            
            for file in files:
                # 1. 检查文件大小
                if file.size > settings.MAX_FILE_SIZE:
                    raise ValueError(f"文件超过限制: {settings.MAX_FILE_SIZE}")
                
                # 2. 检查文件格式
                magic = FileHeaderChecker(file)
                if not magic.is_valid():
                    raise ValueError("无效的文件格式")
                
                # 3. 保存文件
                safe_path = get_safe_path(self.temp_dir, file.filename)
                with open(safe_path, 'wb') as f:
                    content = await file.read()
                    f.write(content)
                
                validated_files.append(FileInfo(
                    name=file.filename,
                    path=safe_path,
                    format=magic.get_format()
                ))
            
            logger.info(f"上传验证成功: {len(validated_files)} 个文件")
            return ApiResponse(code=0, message="上传成功", data={
                "files": validated_files
            })
        
        except Exception as e:
            logger.error(f"上传失败: {str(e)}")
            return ApiResponse(code=400, message=str(e))
```

#### 4.2.4 SILK 文件头处理规范

```python
# app/utils/file_header.py
class FileHeaderChecker:
    """文件头检查和处理"""
    
    SILK_STANDARD_HEADER = b'#!silk_v3'
    SILK_WECHAT_HEADER = b'\x02#!silk_v3'
    SILK_FOOTER = b'\xff\xff'
    
    def __init__(self, file_or_path):
        if isinstance(file_or_path, UploadFile):
            self.data = file_or_path.file.read(10)
        else:
            with open(file_or_path, 'rb') as f:
                self.data = f.read(10)
    
    def is_silk(self) -> bool:
        """检查是否为 SILK 格式"""
        return (self.data.startswith(self.SILK_STANDARD_HEADER) or
                self.data.startswith(self.SILK_WECHAT_HEADER))
    
    def is_wechat_silk(self) -> bool:
        """检查是否为微信 SILK 格式（带 0x02 头）"""
        return self.data.startswith(self.SILK_WECHAT_HEADER)
    
    def normalize_silk(self, input_path: Path, output_path: Path):
        """标准化 SILK 文件（移除微信头，保留标准结构）"""
        with open(input_path, 'rb') as f:
            data = f.read()
        
        # 移除微信头
        if data.startswith(self.SILK_WECHAT_HEADER):
            data = data[1:]  # 移除 0x02
        
        # 移除结尾标记
        if data.endswith(self.SILK_FOOTER):
            data = data[:-2]
        
        with open(output_path, 'wb') as f:
            f.write(data)
```

#### 4.2.5 SILK 编解码服务规范

```python
# app/services/audio_service.py
import subprocess
from pathlib import Path
from app.config import settings
from loguru import logger

class AudioService:
    """音频编解码服务"""
    
    def __init__(self):
        self.decoder_path = Path(settings.SILK_DECODER_BIN)
        self.encoder_path = Path(settings.SILK_ENCODER_BIN)

    async def silk_to_wav(self, silk_path: Path, output_path: Path) -> bool:
        """SILK 解码为 WAV"""
        try:
            # 1. SILK 转 PCM
            pcm_path = output_path.with_suffix('.pcm')
            cmd_decode = [
                str(self.decoder_path),
                str(silk_path),
                str(pcm_path)
            ]
            subprocess.run(cmd_decode, check=True)

            # 2. 使用 ffmpeg 转换为 WAV
            cmd_ffmpeg = [
                'ffmpeg', '-y', '-f', 's16le', '-ar', str(settings.SAMPLE_RATE),
                '-ac', '1', '-i', str(pcm_path), str(output_path)
            ]
            subprocess.run(cmd_ffmpeg, check=True)
            return True
        except Exception as e:
            logger.error(f"解码失败: {e}")
            return False
```
