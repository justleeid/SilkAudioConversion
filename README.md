# silk_encode

Silk 音频格式转换项目，支持本地文件上传转换、暂存区管理、PLIST 处理，以及数据库音频导入。

## 项目概览

这个仓库分为两个主要部分：

- backend：FastAPI 后端，负责文件上传、格式转换、暂存区、数据库音频导入等能力。
- frontend-v2：Vue 3 + TypeScript + Vite 前端，负责上传、任务展示、暂存区操作和数据库音频导入界面。

项目还保留了部分历史前端代码和文档，用于兼容旧版本或作为参考。

## 目录结构

- backend：后端服务
- frontend-v2：当前前端主工程
- frontend：历史前端工程与参考代码
- PRDs：产品、技术和 UI 文档
- tools：SILK 编解码器和相关工具

## 本地启动

### 1. 启动后端

进入 backend 目录后执行：

	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

启动后可访问：

- 健康检查：/health
- API 文档：/docs

### 2. 启动前端

进入 frontend-v2 目录后执行：

	npm install
	npm run dev

默认开发地址为：http://localhost:5173

## 二次开发步骤

如果你要在这个项目基础上继续开发，建议按下面的顺序进行：

1. 拉取最新代码，确认当前分支与远端同步。
2. 先启动 backend 和 frontend-v2，确认基础链路可用。
3. 根据需求修改对应层：
   - 新增接口或业务逻辑，优先改 backend/app/services 和 backend/app/api。
   - 新增页面、组件或交互，优先改 frontend-v2/src 下的 components、pages、stores、api、types。
   - 涉及功能边界、接口字段、验收标准时，先同步 PRDs。
4. 修改数据库相关能力时，先确认 backend/app/config.py 中的数据库配置。
5. 涉及暂存区和下载行为时，注意 backend/app/services/staging_service.py 和 backend/app/api/staging.py 的数据结构。
6. 完成改动后，分别运行后端和前端构建或启动命令，确认无报错再提交。

## 关键开发入口

- 后端主入口：backend/app/main.py
- 转换服务：backend/app/services/audio_service.py
- 转换协调：backend/app/services/convert_service.py
- 暂存区服务：backend/app/services/staging_service.py
- 数据库音频服务：backend/app/services/database_audio_service.py
- 前端任务面板：frontend-v2/src/components/ResultPanel.vue
- 前端数据库导入：frontend-v2/src/components/DbAudioImport.vue

## 文档说明

PRDs 目录下包含产品需求、技术规范和 UI 设计文档。后续新增功能时，建议先更新文档，再同步代码实现。

## 注意事项

- 目前数据库音频导入已接入，音频格式以 WAV 为主。
- SILK 编码器对输入路径长度比较敏感，后端已使用短路径规避相关问题。
- 提交代码前，建议检查 Git 状态，避免把临时文件或无关改动一起提交。
