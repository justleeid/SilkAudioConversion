# SilkAudioConversion

## 项目简介
SilkAudioConversion 是一个面向局域网部署的 Web 音频转换项目，目标是提供 **SILK ↔ WAV/MP3** 双向转换能力，并支持 iOS 预定义语音相关的 PLIST 转换场景。

根据现有 PRDs 文档：
- 产品需求见 `PRDs/PRD.md`
- 技术规范见 `PRDs/development.md`（与 PRD 冲突时以此为准）
- UI 设计见 `PRDs/ui.md`

计划技术栈：
- 前端：Vue 3 + Vite + TypeScript + Element Plus
- 后端：FastAPI + Python
- 音频处理：silk-v3-decoder / silk-v3-encoder / ffmpeg

## 当前目录结构
```text
.
├── .gitignore
├── PRDs/
│   ├── PRD.md
│   ├── development.md
│   └── ui.md
└── README.md
```

## 快速开始（基于 PRDs）
当前仓库以文档规划为主，建议按以下顺序启动开发：

1. **阅读需求与规范**
   - 先读 `PRDs/PRD.md` 了解功能范围
   - 再读 `PRDs/development.md` 确认技术与工程约束
   - 参考 `PRDs/ui.md` 实现统一视觉与交互

2. **初始化项目骨架（建议）**
   - `frontend/`：Vue 3 + Vite + TS
   - `backend/`：FastAPI
   - `tools/`：silk 编解码相关依赖

3. **本地开发建议**
   - 后端先实现上传、格式校验、转换任务接口
   - 前端实现单/多文件上传与进度展示
   - 用 ffmpeg 与 silk 编解码工具完成核心转换链路

4. **后续部署建议**
   - 优先 Docker / Docker Compose
   - 局域网部署并通过 Nginx 反向代理暴露服务
