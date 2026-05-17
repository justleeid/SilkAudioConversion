# silk_encode

项目作用：用于将本地或数据库中的音频采样导入、标准化并转换为 Silk 格式，实现 SILK ↔ WAV/MP3 双向转换，提供上传、批量导入、预览、暂存与转换队列管理能力，便于对历史音频数据进行批量转码、归档与再利用。

Silk 音频格式转换与导入工具。该仓库包含：后端服务（FastAPI）、现代前端（Vue 3 + Vite）、以及用于 Silk 编/解码的本地工具。

## 主要内容概览

- `backend/`：FastAPI 后端，负责文件上传、音频格式识别与转换、任务调度、暂存区管理、以及数据库音频导入接口。
- `frontend-v2/`：当前正在使用的前端工程（Vue 3 + TypeScript + Vite），包含上传、任务列表、暂存区、数据库导入页面等。
- `tools/silk-v3-decoder/`：Silk 编解码器源码与二进制，提供本地编码/解码支持。
- `PRDs/`：产品需求、设计与实现说明文档。

（仓库中保留了一个历史 `frontend/` 目录作为参考；日常开发请以 `frontend-v2/` 为主）

## 快速开始

先决条件：`python3`, `node`/`npm` 或 `pnpm`, `ffmpeg`。

1) 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 可选：在 .env 中配置数据库和 ODBC 驱动等（见下面“配置”）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

默认 API 路径：

- 健康检查：`/health`
- OpenAPI 文档：`/docs`

2) 启动前端（开发）

```bash
cd frontend-v2
npm install
npm run dev
```

默认地址（Vite）：`http://localhost:5173`

## 主要功能与 API 端点

- 文件上传与转换（由 `backend/app/services/audio_service.py` 与 `backend/app/services/convert_service.py` 实现）。
- 暂存区管理（`backend/app/services/staging_service.py`）。
- 数据库音频导入：REST 接口位于 `backend/app/api/db_audio.py`，包含查询、预览与批量导入功能：
	- `GET /api/db-audio/query`：按时间、关键字分页查询数据库记录。
	- `GET /api/db-audio/preview/{audio_id}`：获取并预览单条音频。
	- `POST /api/db-audio/import`：将选定记录导入转换队列/暂存区。
	- 管理接口：`POST /api/db-audio/admin/enable`, `GET /api/db-audio/admin/status` 等（需要管理员模式）。

## 配置要点

- 后端配置位于 `backend/app/config.py`，支持 MySQL 与 SQL Server 两种来源：
	- MySQL：`DB_MYSQL_HOST`、`DB_MYSQL_USER`、`DB_MYSQL_PASSWORD`、`DB_MYSQL_DB` 等。
	- SQL Server（本地同步场景）：`DB_MSSQL_DRIVER`、`DB_MSSQL_SERVER`、`DB_MSSQL_USER`、`DB_MSSQL_PASSWORD`、`DB_MSSQL_DB`、`DB_MSSQL_SCHEMA` 等。
- 请使用只读数据库账号用于列表查询，以避免在列表请求中传输大 BLOB。真正需要时再按需拉取音频内容。

## Silk 编解码与工具

- `tools/silk-v3-decoder/` 包含 encoder/decoder 二进制与源码。后端会调用本地二进制进行 Silk 编码。注意：Silk 编码器对输入路径长度敏感，项目中通过短临时文件名规避该问题（见 `backend/app/services/audio_service.py`）。

## 开发与调试建议

- 本地调试顺序：启动 `backend` → 启动 `frontend-v2` → 在前端界面上传或使用「数据库导入」功能触发流程。
- 日志位置：后端日志目录为 `logs/`，转换输出在 `output/`，上传文件存放在 `uploads/`，临时文件在 `temp/`。
- 在更改数据库访问或 ODBC 驱动配置后，优先在小批量数据上做回归测试（避免大批量失败）。

## 同步与备份说明（供运维参考）

- 如果需要将远端 MySQL 中的数据同步到本地 SQL Server，可采用增量同步策略（基于 `history.created_at` 字段），并仅在必要时拉取音频 BLOB，减小带宽与 IO 压力。相关思路与示例 T-SQL 存档在 `PRDs/` 与项目讨论记录中。

## 贡献与提交规范

- 先在本地确认 `git status` 并使用分支进行开发：

```bash
git checkout -b feat/your-feature
git add -A
git commit -m "feat: 描述你的变更"
```

- 推送并发起 PR 到 `origin/main`。在网络受限时，可先使用 `git stash` 或导出补丁 `git diff > changes.patch` 做备份。

## 参考文件

- 后端入口：[backend/app/main.py](backend/app/main.py)
- 数据库音频服务：[backend/app/services/database_audio_service.py](backend/app/services/database_audio_service.py)
- 前端数据库导入组件：[frontend-v2/src/components/DbAudioImport.vue](frontend-v2/src/components/DbAudioImport.vue)

---

若你希望我把 README 调整为更详细的开发者手册（例如按服务拆分运行与调试步骤，加入常见故障排查与命令），我可以继续扩展。当前更新覆盖了项目结构、启动、配置与关键注意点。

