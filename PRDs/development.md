# Silk 音频格式转换 Web 应用 - 技术规范文档

**版本**: v1.2  
**创建日期**: 2026-03-19  
**最后更新**: 2026-05-09  
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
| UI 组件库 | Naive UI | 2.x | Tree-shaking 按需引入，TypeScript 原生支持，内置暗色模式，视觉风格现代克制 |
| 语言 | TypeScript | 5.x | 类型安全，减少运行时错误 |
| 状态管理 | Pinia | 2.x | Vue 3 官方推荐，轻量 |
| 样式方案 | Tailwind CSS | 3.x | 原子化 CSS，与 Naive UI 互补处理自定义布局与间距 |
| HTTP 客户端 | Axios | 1.x | 成熟稳定，拦截器支持 |
| 文件上传 | Naive UI Upload | 2.x | 与 UI 组件库一致，支持拖拽与自定义上传流程 |
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
│   └── Silk 音频转换器 - UI 设计规范.md
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

```vue
<!-- 组件文件结构 (src/components/MyComponent.vue) -->
<template>
  <!-- 布局使用 Tailwind 原子类，组件使用 Naive UI -->
  <div class="flex items-center gap-3 p-4 rounded-lg bg-white dark:bg-gray-800">
    <n-button type="primary" @click="handleClick">操作</n-button>
  </div>
</template>

<script setup lang="ts">
// 导入 — Naive UI 组件按需引入，自动 tree-shaking
import { ref } from 'vue'
import { NButton } from 'naive-ui'
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
/* 仅在 Tailwind 无法覆盖的细节处使用 scoped CSS（如动画、滚动条等） */
</style>
```

**样式分工原则：**
- **Tailwind CSS**：布局（flex/grid）、间距（p-/m-/gap-）、颜色（text-/bg-）、响应式断点
- **Naive UI**：表单、表格、弹窗、通知、标签等交互组件
- **`<style scoped>`**：仅用于 Tailwind 无法覆盖的自定义动画、滚动条、第三方覆写等少数场景

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
            
            # 2. PCM 转 WAV（使用 ffmpeg）
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-f', 's16le',
                '-ar', '24000',
                '-ac', '1',
                '-i', str(pcm_path),
                str(output_path)
            ]
            subprocess.run(cmd_ffmpeg, check=True)
            
            # 3. 清理临时文件
            pcm_path.unlink()
            
            logger.info(f"SILK 转 WAV 成功: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"SILK 转 WAV 失败: {str(e)}")
            return False
```

### 4.3 日志规范

```python
# app/logger.py
import sys
from loguru import logger
from app.config import settings

# 移除默认处理器
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)

# 添加文件输出
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    rotation="500 MB",
    retention="7 days"
)
```

---

## 5. API 设计规范

### 5.1 RESTful 规范

- 使用 HTTP 方法表示操作：GET (查询)、POST (创建/执行)、DELETE (删除)
- 路径参数使用花括号：`/api/convert/{taskId}`
- 使用 HTTP 状态码：200 (成功)、400 (请求错误)、404 (未找到)、500 (服务器错误)
- 版本号可选，推荐在路径中体现：`/api/v1/convert`

### 5.2 统一响应格式

所有 API 响应遵循此格式：

```json
{
  "code": 0,
  "message": "操作成功",
  "data": {}
}
```

- `code`: 0 表示成功，其他值为错误码
- `message`: 人类可读的消息
- `data`: 响应数据，可选

### 5.3 错误码规范

| 错误码 | 含义 | HTTP 状态码 |
|--------|------|-----------|
| 0 | 成功 | 200 |
| 400 | 请求参数错误 | 400 |
| 401 | 未授权 | 401 |
| 403 | 禁止访问 | 403 |
| 404 | 资源不存在 | 404 |
| 413 | 文件过大 | 413 |
| 500 | 服务器错误 | 500 |
| 1001 | 无效的 SILK 文件头 | 400 |
| 1002 | 不支持的文件格式 | 400 |
| 1003 | 转换失败 | 500 |

### 5.4 转换请求参数约束

`POST /api/convert/{taskId}` 请求体定义：

```json
{
  "targetFormat": "WAV",
  "wechatCompatible": true,
  "sampleRate": 24000,
  "bitRate": 24000,
  "frameSize": 20
}
```

- `wechatCompatible`: 布尔值，默认 `true`
  - 当 `true` 时：输出微信兼容 SILK（添加 `0x02` 头，移除 `b'\xff\xff'` 尾标记）
  - 当 `false` 时：输出标准 SILK（不添加 `0x02` 头，保留标准结构）

---

## 6. 安全规范

### 6.1 文件上传安全

```python
# app/middleware/security.py
import os
from pathlib import Path
from fastapi import UploadFile

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {'.silk', '.wav', '.mp3', '.amr'}

def validate_upload(file: UploadFile) -> bool:
    """验证上传文件"""
    # 1. 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise ValueError(f"文件过大，最大 {MAX_FILE_SIZE / 1024 / 1024:.0f}MB")
    
    # 2. 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {file_ext}")
    
    # 3. 检查文件魔数
    from python_magic import Magic
    mime = Magic(mime=True)
    file_type = mime.from_buffer(file.file.read(1024))
    
    # 验证文件类型
    valid_types = ['audio/x-silk', 'audio/wav', 'audio/mpeg', 'audio/amr']
    if not any(t in file_type for t in valid_types):
        raise ValueError("文件内容与扩展名不匹配")
    
    file.file.seek(0)  # 重置文件指针
    return True
```

### 6.2 目录访问控制

```python
# app/utils/path_security.py
from pathlib import Path

def get_safe_path(base_dir: Path, filename: str) -> Path:
    """获取安全的文件路径"""
    # 1. 禁止路径遍历
    if '..' in filename or filename.startswith('/'):
        raise ValueError("非法文件名")
    
    # 2. 构建安全路径
    safe_path = (base_dir / filename).resolve()
    
    # 3. 验证路径在允许范围内
    if not str(safe_path).startswith(str(base_dir.resolve())):
        raise ValueError("文件路径超出允许范围")
    
    return safe_path
```

### 6.3 CORS 配置

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)
```

---

## 7. 配置管理

### 7.1 环境变量配置

```bash
# .env.example
# 服务器配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 文件上传配置
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
OUTPUT_DIR=./output
MAX_FILE_SIZE=52428800
MAX_FILE_COUNT=50

# SILK 工具路径
SILK_DECODER_BIN=./tools/silk-v3-decoder/silk_v3_decoder
SILK_ENCODER_BIN=./tools/silk-v3-encoder/silk_v3_encoder

# 任务队列配置
MAX_CONCURRENT_TASKS=5
TASK_TIMEOUT=3600

# 暂存区配置
CACHE_EXPIRE_HOURS=48
CACHE_CLEANUP_INTERVAL=3600

# 数据库配置
DB_AUDIO_HOST=localhost
DB_AUDIO_PORT=3306
DB_AUDIO_USER=root
DB_AUDIO_PASSWORD=
DB_AUDIO_NAME=ai_agent
DB_AUDIO_TABLE=ai_agent_chat_audio
DB_HISTORY_TABLE=ai_agent_chat_history
```

### 7.2 Python 配置类

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
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
    silk_decoder_bin: str = "./tools/silk-v3-decoder/silk_v3_decoder"
    silk_encoder_bin: str = "./tools/silk-v3-encoder/silk_v3_encoder"
    
    # 任务队列配置
    max_concurrent_tasks: int = 5
    task_timeout: int = 3600
    
    # 暂存区配置
    cache_expire_hours: int = 48
    cache_cleanup_interval: int = 3600
    
    # 数据库配置
    db_audio_host: str = "localhost"
    db_audio_port: int = 3306
    db_audio_user: str = "root"
    db_audio_password: str = ""
    db_audio_name: str = "ai_agent"
    db_audio_table: str = "ai_agent_chat_audio"
    db_history_table: str = "ai_agent_chat_history"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## 7.3 数据库音频导入服务

### 7.3.1 数据库连接与查询

```python
# app/services/database_audio_service.py
from typing import Optional
import mysql.connector
from loguru import logger
from app.config import settings

class DatabaseAudioService:
    """数据库音频查询导入服务"""
    
    def __init__(self):
        self.host = settings.db_audio_host
        self.port = settings.db_audio_port
        self.user = settings.db_audio_user
        self.password = settings.db_audio_password
        self.database = settings.db_audio_name
    
    def get_connection(self):
        """获取数据库连接"""
        conn = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return conn
    
    async def query_audio_records(
        self,
        date_start: str,
        date_end: str,
        keyword: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """查询数据库中的音频记录 (chat_type=2, WAV 格式已验证)"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询 SQL
        query = f"""
            SELECT 
                a.id as audio_id,
                SUBSTRING(h.content, 1, 50) as title,
                DATE_FORMAT(h.created_at, '%Y-%m-%d %H:%i:%s') AS created_at,
                LENGTH(a.audio) as size
            FROM {settings.db_history_table} h
            JOIN {settings.db_audio_table} a ON h.audio_id = a.id
            WHERE h.created_at >= %s AND h.created_at <= %s
            AND h.chat_type = 2
        """
        
        params = [f"{date_start} 00:00:00", f"{date_end} 23:59:59"]
        
        if keyword:
            query += " AND h.content LIKE %s"
            params.append(f"%{keyword}%")
        
        # 分页
        offset = (page - 1) * per_page
        query += " ORDER BY h.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        logger.info(f"查询数据库音频: {len(records)} 条")
        
        cursor.close()
        conn.close()
        
        return {"records": records}
    
    async def get_audio_blob(self, audio_id: str) -> bytes:
        """获取音频 blob 数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            f"SELECT audio FROM {settings.db_audio_table} WHERE id = %s",
            (audio_id,)
        )
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise ValueError(f"音频 {audio_id} 不存在")
        
        return result[0]
```

### 7.3.2 数据库音频导入 API 端点

```python
# app/api/db_audio.py
from fastapi import APIRouter, Query
from typing import Optional
from pydantic import BaseModel
from app.services.database_audio_service import DatabaseAudioService
from app.models.response import ApiResponse
from loguru import logger

router = APIRouter(prefix="/api/db-audio", tags=["database_audio"])

class ImportRequest(BaseModel):
    audio_ids: list[str]

@router.get("/query")
async def query_database_audio(
    date_start: str = Query(...),
    date_end: str = Query(...),
    keyword: Optional[str] = Query(None),
    page: int = Query(1),
    per_page: int = Query(20)
):
    """查询数据库音频记录"""
    try:
        service = DatabaseAudioService()
        result = await service.query_audio_records(date_start, date_end, keyword, page, per_page)
        return ApiResponse(code=0, message="查询成功", data=result)
    except Exception as e:
        logger.error(f"查询失败: {str(e)}")
        return ApiResponse(code=400, message=str(e))

@router.post("/import")
async def import_database_audio(request: ImportRequest):
    """导入数据库音频"""
    try:
        if not request.audio_ids:
            return ApiResponse(code=400, message="没有选择任何音频")
        
        db_service = DatabaseAudioService()
        
        tasks = []
        for audio_id in request.audio_ids:
            try:
                audio_blob = await db_service.get_audio_blob(audio_id)
                # 保存临时文件并创建转换任务
                # 实现细节由 ConvertService 处理
                tasks.append({"task_id": audio_id, "source": "database"})
            except Exception as e:
                logger.error(f"处理 {audio_id} 失败: {str(e)}")
        
        return ApiResponse(code=0, message="导入成功", data={"imported_count": len(tasks)})
    except Exception as e:
        logger.error(f"导入失败: {str(e)}")
        return ApiResponse(code=500, message=str(e))

# app/main.py 中注册路由:
# from app.api import db_audio
# app.include_router(db_audio.router)
```

---

## 8. 部署规范

### 8.1 Docker 部署（推荐）

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - MAX_CONCURRENT_TASKS=5
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/temp:/app/temp
      - ./backend/output:/app/output
    networks:
      - silk_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - silk_network

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - silk_network

networks:
  silk_network:
    driver: bridge
```

### 8.2 本地开发部署

```bash
# 后端启动
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端启动（新终端）
cd frontend
npm install
npm run dev
```

---

## 9. 测试规范

### 9.1 后端测试

```python
# tests/test_audio_service.py
import pytest
from pathlib import Path
from app.services import AudioService

@pytest.mark.asyncio
async def test_silk_to_wav():
    """测试 SILK 转 WAV"""
    service = AudioService()
    
    # 使用测试文件
    input_file = Path("tests/fixtures/test.silk")
    output_file = Path("tests/output/test.wav")
    
    result = await service.silk_to_wav(input_file, output_file)
    
    assert result is True
    assert output_file.exists()
```

### 9.2 前端测试

```typescript
// tests/api.test.ts
import { describe, it, expect, vi } from 'vitest'
import { convertApi } from '@/api/convert'

describe('Convert API', () => {
  it('should upload files successfully', async () => {
    const files = [new File(['content'], 'test.silk')]
    
    // Mock 请求
    vi.mock('@/api/convert', () => ({
      convertApi: {
        upload: vi.fn().mockResolvedValue({
          code: 0,
          message: '上传成功'
        })
      }
    }))
    
    const result = await convertApi.upload(files)
    expect(result.code).toBe(0)
  })
})
```

---

## 10. 禁止事项清单

| ❌ 禁止 | ✅ 替代方案 |
|--------|-----------|
| 手动解析文件头 | 使用 `FileHeaderChecker` 类 |
| 直接拼接文件路径 | 使用 `get_safe_path()` 函数 |
| 硬编码配置值 | 使用 `settings` 配置类 |
| 直接调用 `subprocess` | 封装到 `Service` 类中 |
| 返回原始异常 | 使用统一响应格式 |
| 在前端存储敏感信息 | 所有敏感数据在后端处理 |
| 使用 `eval/exec` | 使用安全解析库 |
| 直接操作文件系统 | 使用 `FileService` 封装 |
| 忽略日志记录 | 所有关键操作记录日志 |
| 使用云存储/云服务 | 全部本地存储 |

---

## 11. 开发检查清单

### 11.1 提交前检查

- [ ] 代码符合规范，已通过 linter
- [ ] 添加了必要的日志记录
- [ ] 错误处理完整，使用统一响应格式
- [ ] 文件操作使用了安全函数
- [ ] 没有硬编码配置值，已移至环境变量
- [ ] 添加了单元测试
- [ ] 没有遗留的 console.log 或 print

### 11.2 代码审查要点

- [ ] 是否使用了成熟组件库
- [ ] 是否有重复造轮子的代码
- [ ] 文件上传是否有完整验证
- [ ] 路径处理是否安全
- [ ] 日志是否完整
- [ ] 配置是否从环境变量读取
- [ ] 错误处理是否统一
- [ ] 类型定义是否完整

---

## 12. 附录

### 12.1 依赖版本锁定

```
# backend/requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
python-magic==0.4.27
loguru==0.7.0
pydantic-settings==2.1.0
python-jose==3.3.0
```

```
# frontend/package.json (核心依赖)
vue: 3.4.x
naive-ui: 2.x
tailwindcss: 3.x
pinia: 2.x
axios: 1.x
typescript: 5.x
```

### 12.2 参考文档

| 文档 | 链接 |
|------|------|
| FastAPI 官方文档 | https://fastapi.tiangolo.com/ |
| Vue 3 官方文档 | https://vuejs.org/ |
| Naive UI 文档 | https://www.naiveui.com/ |
| Tailwind CSS 文档 | https://tailwindcss.com/ |
| silk-v3-decoder | https://github.com/kn007/silk-v3-decoder |
| ffmpeg 文档 | https://ffmpeg.org/documentation.html |

---

## 13. 文档协同与变更流程

### 13.1 文档优先级

1. **development.md**：技术规范优先级最高
   - 定义技术栈、目录结构、API 风格、配置方式、安全规范、部署口径
2. **PRD.md**：产品需求文档
   - 定义需求边界与业务验收标准
3. **Silk 音频转换器 - UI 设计规范.md**：UI 设计规范
   - 定义视觉交互与组件表现

**任何功能、接口、配置、部署、安全实现，必须先满足本技术规范。**

### 13.2 跨文档同步规则

1. 当接口结构、字段命名、状态枚举变化时：先更新 development.md，再同步 PRD.md 与 Silk 音频转换器 - UI 设计规范.md
2. 当新增业务能力时：先更新 PRD.md，再补充 development.md，最后更新 Silk 音频转换器 - UI 设计规范.md
3. 当仅视觉风格变化时：更新 Silk 音频转换器 - UI 设计规范.md，同时检查 PRD.md 与 development.md 引用是否失效

### 13.3 联动验收清单

- [ ] API 路径风格保持一致（路径参数统一使用花括号）
- [ ] 统一响应结构保持一致（code/message/data）
- [ ] 配置来源保持一致（环境变量 + settings）
- [ ] 部署口径保持一致（根目录 docker-compose.yml + backend/frontend 服务）
- [ ] UI 展示状态与后端状态枚举一致

---

**本文档是开发的权威指南，所有团队成员必须严格遵守。**
