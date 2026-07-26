# Silk 音频转换器

将本地或数据库中的音频采样导入、标准化并转换为 SILK 格式，实现 **SILK ↔ WAV/MP3 双向转换**，支持上传、批量导入、预览、PLIST 打包/拆分、暂存与转换队列管理。

## 功能概览

| 功能 | 说明 |
|------|------|
| 🎵 音频上传 | 单/多文件上传，拖拽支持，格式/大小自动校验 |
| 🔄 SILK 解码 | SILK → WAV / MP3（自动处理微信 0x02 头） |
| 🔀 SILK 编码 | WAV / MP3 / AMR / M4A → SILK（可配采样率、比特率、帧大小、微信兼容） |
| 📦 PLIST 打包 | 多个 SILK 合并为 iOS 预定义语音 PLIST / PLIST 拆分为 SILK |
| ✂️ PLIST 拆分 | 将成品 PLIST 均匀或手动拆分为多个独立文件 |
| 🗄️ 暂存区 | 转换结果暂存 48h，支持下载、重命名、批量删除、自动清理 |
| 🗃️ 数据库导入 | 从 MySQL / SQL Server 按时间、关键字查询并批量导入音频 |
| 🔧 管理功能 | 数据库记录删除、标题修改（需手动启用管理员模式） |

## 目录结构

```
silk_encode/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # REST 路由（convert / plist / staging / config / db-audio）
│   │   ├── services/     # 业务逻辑（audio / convert / file / plist / staging / database-audio）
│   │   ├── models/       # 数据模型
│   │   ├── utils/        # 工具（file_header / path_security）
│   │   ├── config.py     # 配置类（.env 驱动）
│   │   ├── logger.py     # loguru 日志配置
│   │   └── main.py       # 入口
│   ├── .env.example
│   └── requirements.txt
├── frontend-v2/          # Vue 3 前端
│   ├── src/
│   │   ├── components/   # FileInputPanel / ConvertPanel / ResultPanel / DbAudioImport 等
│   │   ├── pages/        # HomePage
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── api/          # HTTP 客户端
│   │   ├── types/        # TypeScript 类型定义
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── deploy/               # 部署脚本（Windows .bat / PowerShell）
├── tools/
│   └── silk-v3-decoder/  # SILK 编解码器（Git submodule）
├── PRDs/                 # 产品需求与技术规范文档
└── README.md
```

## 快速开始

**先决条件：** `python3`、`node`/`npm`、`ffmpeg`

### 1) 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 填入数据库等配置

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 健康检查：`http://localhost:8000/health`
- API 文档：`http://localhost:8000/docs`

### 2) 启动前端

```bash
cd frontend-v2
npm install
npm run dev
```

- 默认地址：`http://localhost:5173`

## API 端点一览

| 端点 | 说明 |
|------|------|
| `POST /api/upload` | 上传音频文件 |
| `POST /api/convert/{task_id}` | 执行转换 |
| `GET /api/convert/{task_id}/status` | 查询转换状态 |
| `GET /api/download/{task_id}` | 下载转换结果 |
| `POST /api/plist/merge` | 合并多个 SILK 为 PLIST |
| `POST /api/plist/extract` | 从 PLIST 提取 SILK |
| `GET /api/plist/preview/{file_id}` | 预览 PLIST 条目 |
| `POST /api/plist/split` | 拆分 PLIST |
| `GET /api/staging` | 查看暂存区 |
| `DELETE /api/staging/{file_id}` | 删除暂存文件 |
| `POST /api/staging/{file_id}/rename` | 重命名暂存文件 |
| `POST /api/staging/cleanup` | 手动清理过期文件 |
| `GET /api/db-audio/query` | 查询数据库音频 |
| `POST /api/db-audio/import` | 导入数据库音频 |
| `GET /api/db-audio/preview/{audio_id}` | 预览播放数据库音频 |
| `GET /api/config` | 获取当前配置 |

## 配置

后端配置通过 `.env` 文件或环境变量注入，关键项：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | `0.0.0.0` | 监听地址 |
| `PORT` | `8000` | 监听端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `MAX_FILE_SIZE` | `209715200` | 上传大小上限（字节） |
| `MAX_FILE_COUNT` | `50` | 单次上传文件数上限 |
| `SILK_DECODER_BIN` | `./tools/.../decoder` | 解码器路径 |
| `SILK_ENCODER_BIN` | `./tools/.../encoder` | 编码器路径 |
| `DB_*` | — | MySQL / SQL Server 连接配置 |

## SILK 格式说明

**标准 SILK：**
- 开头：`#!silk_v3`（9 字节）
- 结尾：`\xff\xff`（2 字节）

**微信 SILK：**
- 开头：`\x02` + `#!silk_v3`（10 字节）
- 结尾：无 `\xff\xff`

系统自动检测并处理微信头，`wechat_compatible` 开关控制编码时是否添加微信头。

## 开发与调试

- 调试顺序：**后端 → 前端** → 在界面上传或使用「数据库导入」触发流程
- 日志目录：`backend/logs/`
- 输出目录：`backend/output/`
- 上传暂存：`backend/uploads/` / `backend/temp/`
- 子模块初始化：`git submodule update --init --recursive`

## License

MIT
