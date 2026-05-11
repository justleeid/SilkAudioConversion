# Silk 音频格式转换 Web 应用 - 产品需求文档

**版本**: v3.3  
**创建日期**: 2026-03-19  
**最后更新**: 2026-05-09  
**状态**: ✅ 已完成，可用于开发

---

## 1. 项目概述

### 1.1 项目背景

微信、Skype、QQ 等通讯软件使用 SILK 音频编码格式，该格式无法在常规播放器中播放。现有的 silk-v3-decoder 项目仅支持客户端命令行方式运行，缺乏 Web 界面。

本项目旨在构建一个**前后端分离的 Web 应用**，实现 SILK 格式与其他音频格式的**双向转换**。

### 1.2 项目目标

| 目标 | 描述 |
|------|------|
| 核心功能 | 实现 SILK ↔ WAV/MP3 双向转换 |
| 用户体验 | 提供简洁的 Web 界面，支持移动端访问 |
| 部署方式 | 局域网部署，无需外网依赖，无需登录 |
| 安全要求 | 基础安全配置，文件访问控制，可配置日志 |
| 特殊场景 | 支持 iOS 预定义语音打包为 PLIST |

### 1.3 技术选型（已确认）

**前端:**
- Vue 3 + Vite + TypeScript
- UI 组件库: Naive UI（v2.x）
- 样式: Tailwind CSS
- 状态管理: Pinia

**后端:**
- Python (FastAPI) + Anaconda/venv 虚拟环境

**音频处理:**
- silk-v3-decoder + silk-v3-encoder + ffmpeg

**存储:**
- 本地文件系统 + 临时存储区

**部署:**
- Docker 或直接部署 + Nginx 反向代理

> ⚠️ **说明**: 当 PRD 与技术规范存在冲突时，**以 development.md 为准**。

---

## 2. 功能需求

### 2.1 核心功能模块

#### 2.1.1 音频上传模块

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| 单文件上传 | 支持拖拽或点击选择单个音频文件 | P0 |
| 多文件上传 | 支持批量选择多个文件（建议上限 50 个） | P0 |
| 格式检测 | 自动识别上传文件格式（silk/wav/mp3/amr 等） | P0 |
| 大小限制 | 可配置上传大小限制（默认 50MB/文件） | P0 |
| 格式限制 | 仅允许指定格式上传，拒绝非法文件 | P0 |

#### 2.1.2 SILK 转普通格式（解码）

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| SILK → WAV | 转换为标准 WAV 格式（16bit PCM） | P0 |
| SILK → MP3 | 转换为 MP3 格式（可配置比特率） | P0 |
| 微信头处理 | 自动检测并处理 0x02 文件头字节 | P0 |
| 结尾处理 | 检测并处理 `b'\xff\xff'` 结尾标记 | P0 |
| 批量转换 | 支持多文件队列转换 | P1 |

#### 2.1.3 普通格式转 SILK（编码）

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| WAV → SILK | 转换为微信兼容的 SILK 格式 | P0 |
| MP3 → SILK | 转换为微信兼容的 SILK 格式 | P0 |
| 采样率配置 | 支持 8kHz/16kHz/24kHz 采样率选择 | P0 |
| 比特率配置 | 支持 SILK 编码比特率配置 | P2 |
| 微信头添加 | 转换后自动添加 0x02 文件头，移除 `b'\xff\xff'` | P0 |
| 帧大小配置 | 支持 20ms/40ms/60ms 帧大小选择 | P2 |
| 微信兼容方式 | 可选开关：开启输出微信兼容 SILK；关闭输出标准 SILK | P0 |

#### 2.1.4 PLIST 转换模块（iOS 预定义语音）

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| SILK → PLIST | 将 SILK 文件转为 Apple XML plist 格式 | P1 |
| 多文件合并 | 多个 SILK 合并为一个 plist 文件 | P1 |
| PLIST → SILK | 从 plist 还原为原始 SILK 文件 | P1 |
| 格式规范 | `<key>文件名</key><string>base64 内容</string>` | P1 |
| iOS 兼容 | 符合 iOS NSBundle 资源加载规范 | P1 |
| 元数据支持 | 可选添加 duration、sampleRate 等元数据 | P2 |

#### 2.1.5 暂存区模块

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| 临时存储 | 转换结果暂存 48 小时（可配置） | P1 |
| 下载链接 | 生成唯一下载链接 | P1 |
| 跨端访问 | 同一局域网内其他设备可下载 | P1 |
| 自动清理 | 定时清理过期文件 | P1 |

#### 2.1.6 通知模块

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| 转换完成通知 | 前端弹窗/消息提示 | P1 |
| 进度显示 | 实时显示转换进度百分比 | P1 |
| 错误通知 | 转换失败时显示错误原因 | P1 |

#### 2.1.7 日志模块

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| 日志开关 | 可配置开启/关闭日志记录 | P1 |
| 日志级别 | 支持 INFO/WARNING/ERROR 等级别 | P1 |
| 日志内容 | 记录上传、转换、下载等操作 | P1 |
| 日志存储 | 本地文件存储，可配置轮转策略 | P1 |

#### 2.1.8 数据库音频导入模块

| 功能项 | 详细描述 | 优先级 |
|--------|----------|--------|
| 数据库连接 | 连接到 AI Agent 数据库，配置在 .env 中 | P1 |
| 时间范围查询 | 按 created_at 查询指定时间范围内的音频记录 | P1 |
| 关键字搜索 | 按 content 字段前 N 个字作为标题进行搜索 | P1 |
| 批量导入 | 支持多选批量导入到转换队列 | P1 |
| 格式检测 | 自动检测数据库中 audio blob 的格式（当前为 WAV） | P1 |
| 来源标记 | 转换后的文件用 `[DB]` 前缀标记数据库来源 | P1 |
| 暂存区区分 | 暂存区显示不同的图标或颜色区分导入来源 | P1 |
| 元数据保留 | 记录原始 audio_id、session_id 等关键信息 | P2 |

---

## 3. SILK 格式技术细节（已确认）

### 3.1 文件头结构对比

**标准 SILK 文件格式**
```
开头: b'#!silk_v3' (9 字节)
结尾: b'\xff\xff' (2 字节)
内容: SILK 编码音频数据
```

**微信 SILK 文件格式**
```
开头: b'\x02' + b'#!silk_v3' (10 字节)
结尾: 无 b'\xff\xff' 标记
内容: SILK 编码音频数据
```

### 3.2 编码/解码处理流程

**SILK 解码流程（微信 SILK → WAV/MP3）**

```python
def decode_wechat_silk(input_file, output_file, output_format='wav'):
    """SILK 解码为 WAV/MP3"""
    # 1. 读取文件
    data = read_file(input_file)
    
    # 2. 检测并移除微信文件头 0x02
    if data.startswith(b'\x02#!silk_v3'):
        data = data[1:]  # 移除 0x02
        is_wechat = True
    elif data.startswith(b'#!silk_v3'):
        is_wechat = False
    else:
        raise Error("无效的 SILK 文件头")
    
    # 3. 检测并移除结尾标记（如果存在）
    if data.endswith(b'\xff\xff'):
        data = data[:-2]
    
    # 4. 写入临时 SILK 文件
    temp_silk = write_temp_file(data)
    
    # 5. 使用 silk-v3-decoder 解码为 PCM
    pcm_file = run_decoder(temp_silk)
    
    # 6. 使用 ffmpeg 转换为 WAV/MP3
    ffmpeg_convert(pcm_file, output_file, output_format)
    
    return output_file
```

**SILK 编码流程（WAV/MP3 → 微信 SILK）**

```python
def encode_wechat_silk(input_file, output_file, sample_rate=24000, 
                       bit_rate=24000, frame_size=20):
    """WAV/MP3 编码为微信兼容 SILK"""
    # 1. 使用 ffmpeg 转换为 PCM（16bit 单声道）
    pcm_file = ffmpeg_to_pcm(input_file, sample_rate)
    
    # 2. 使用 silk-v3-encoder 编码为 SILK
    silk_file = run_encoder(pcm_file, sample_rate, bit_rate, frame_size)
    
    # 3. 读取 SILK 文件内容
    data = read_file(silk_file)
    
    # 4. 移除结尾标记（如果存在）
    if data.endswith(b'\xff\xff'):
        data = data[:-2]
    
    # 5. 添加微信文件头 0x02
    data = b'\x02' + data
    
    # 6. 写入输出文件
    write_file(output_file, data)
    
    return output_file
```

### 3.3 采样率与场景对照表

| 采样率 | 比特率 | 帧大小 | 适用场景 | 文件大小 | 音质 |
|---------|---------|---------|-----------|----------|------|
| 8 kHz | 8-12 kbps | 20ms | 语音通话，最低带宽 | 最小 | 一般 |
| 16 kHz | 16-20 kbps | 20ms | 微信语音默认 | 中等 | 良好 |
| 24 kHz | 24-32 kbps | 20ms | 高质量语音，iOS 预定义 | 最大 | 优秀 |

### 3.4 PLIST 格式规范（iOS 预定义语音）

**单文件示例**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>voice_001.silk</key>
    <string>base64_encoded_content_1</string>
</dict>
</plist>
```

**多文件示例**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>voice_001.silk</key>
    <string>base64_encoded_content_1</string>
    <key>voice_002.silk</key>
    <string>base64_encoded_content_2</string>
    <key>voice_003.silk</key>
    <string>base64_encoded_content_3</string>
</dict>
</plist>
```

---

## 4. 技术架构

### 4.1 系统架构图

```
┌─────────────────────────────────────────┐
│           前端 (Vue 3)                  │
│  文件上传 │ 转换配置 │ 进度展示 │ 下载   │
└──────────────────┬──────────────────────┘
                   ↓ HTTP/REST API
┌─────────────────────────────────────────┐
│        后端 (Python FastAPI)            │
│  文件接收 │ 格式检测 │ 转换调度 │ 存储   │
│  日志模块 │ 配置管理 │ 任务队列          │
└──────────────────┬──────────────────────┘
                   ↓ 子进程
┌─────────────────────────────────────────┐
│        音频处理引擎                     │
│  silk-v3-decoder │ silk-v3-encoder      │
│  ffmpeg (PCM ↔ MP3/WAV)                 │
└─────────────────────────────────────────┘
```

### 4.2 目录结构

参考 development.md 第 3.1 节。

---

## 5. API 接口设计

### 5.1 上传接口

**POST /api/upload**

```json
请求: multipart/form-data
- files: File[]

响应:
{
  "code": 0,
  "message": "上传成功",
  "data": {
    "files": [
      {
        "taskId": "abc123",
        "filename": "voice_001.silk",
        "size": 1024,
        "format": "silk"
      }
    ]
  }
}
```

### 5.2 转换接口

**POST /api/convert/{taskId}**

```json
请求:
{
  "targetFormat": "WAV",
  "wechatCompatible": true,
  "sampleRate": 24000,
  "bitRate": 24000,
  "frameSize": 20
}

响应:
{
  "code": 0,
  "message": "转换成功",
  "data": {
    "downloadUrl": "http://localhost:8000/api/download/xyz789"
  }
}
```

### 5.3 查询转换状态

**GET /api/convert/{taskId}/status**

```json
响应:
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "status": "processing",
    "progress": 65,
    "estimatedTime": 3
  }
}
```

### 5.4 下载接口

**GET /api/download/{fileId}**

返回文件流，文件自动清理后返回 404。

### 5.5 PLIST 专用接口

**POST /api/plist/merge**

```json
请求:
{
  "taskIds": ["abc123", "def456"],
  "outputFilename": "voices.plist",
  "includeMetadata": true
}

响应:
{
  "code": 0,
  "message": "合并成功",
  "data": {
    "downloadUrl": "http://localhost:8000/api/download/plist123"
  }
}
```

### 5.6 文件管理接口

**GET /api/staging** - 查看暂存区

**DELETE /api/staging/{fileId}** - 删除暂存文件

**POST /api/staging/cleanup** - 手动清理过期文件

### 5.7 配置接口

**GET /api/config** - 获取当前配置

返回：支持格式、大小限制、采样率选项等。

### 5.8 数据库音频导入接口

**GET /api/db-audio/query**

查询数据库中的音频记录

```json
请求参数:
{
  "date_start": "2026-05-01",
  "date_end": "2026-05-10",
  "keyword": "喜欢",
  "page": 1,
  "per_page": 20
}

响应:
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "total": 12,
    "records": [
      {
        "audio_id": "8733d7dca1e247e8b6331e0efa4f52d0",
        "title": "喜欢真诚的人",
        "created_at": "2026-05-05T23:59:44.231279",
        "size": 32684,
        "format": "wav",
        "session_id": "session_123",
        "mac_address": "00:11:22:33:44:55"
      }
    ]
  }
}
```

**POST /api/db-audio/import**

导入选定的数据库音频到转换队列

```json
请求:
{
  "audio_ids": ["8733d7dca1e247e8b6331e0efa4f52d0", "fccda731ee3c45789c9ce7177b1b941b"]
}

响应:
{
  "code": 0,
  "message": "导入成功",
  "data": {
    "imported_count": 2,
    "tasks": [
      {
        "task_id": "uuid1",
        "original_name": "[DB] 喜欢真诚的人",
        "size": 32684,
        "format": "wav",
        "source": "database",
        "source_audio_id": "8733d7dca1e247e8b6331e0efa4f52d0"
      }
    ]
  }
}
```

---

## 6. 配置管理

### 6.1 环境变量配置 (.env)

参考 development.md 第 7.1 节。

---

## 7. 前端页面设计

### 7.1 页面结构

参考 Silk 音频转换器 - UI 设计规范.md 第 4 节。

### 7.2 数据库导入窗口

**功能描述:**

在上传区域旁边或下方添加"数据库导入"标签页/窗口，供用户查询和导入数据库中的音频。

**UI 布局:**

```
┌──────────────────────────────────────────┐
│ 转换方式: [ 本地上传 ] [ 数据库导入 ]      │
├──────────────────────────────────────────┤
│ 筛选条件:                               │
│   时间范围: [2026-05-01] 至 [2026-05-10] │
│   关键字:   [搜索音频内容...]             │
│   [查询] [清空]                          │
├──────────────────────────────────────────┤
│ 查询结果 (可多选，共 12 条):             │
│ ☐ 喜欢真诚的人          32.6 KB         │
│ ☐ 够钟                 42.5 KB          │
│ ☐ 霍希                 74.2 KB          │
│ ... (分页显示)                          │
│ [批量导入(3)] [预览] [详情]              │
└──────────────────────────────────────────┘
```

**功能说明:**
- 时间范围过滤：按 created_at 日期范围查询
- 关键字搜索：按 content 字段模糊匹配（可选）
- 多选导入：支持选择多个音频批量导入
- 来源标记：导入后的文件名自动添加 `[DB]` 前缀

### 7.3 暂存区来源区分

**文件来源标记**

```
暂存区显示示例:
┌─────────────────────────────────────────┐
│ 暂存区 (6个文件 | 393.4 KB | 48h后)      │
├─────────────────────────────────────────┤
│ 歌曲1_converted.silk              (本地)│
│ 🔹 喜欢真诚的人_converted.silk    (DB) │
│ 🔹 够钟_converted.silk            (DB) │
│ 歌曲2_converted.silk              (本地)│
│ ...                                    │
└─────────────────────────────────────────┘

说明:
- 文件名前缀 [DB] 表示来自数据库导入
- 蓝色圆点 🔹 作为视觉标记区分来源
```

### 7.4 移动端适配

参考 Silk 音频转换器 - UI 设计规范.md 第 8 节。

---

## 8. 安全配置

### 8.1 服务端安全

- 文件上传大小限制：50MB/文件
- 支持格式白名单：.silk, .wav, .mp3, .amr
- 文件魔数检验，防止绕过
- 路径安全检查，防止目录遍历
- 速率限制：可配置

参考 development.md 第 6 节。

### 8.2 日志安全

- 日志不记录敏感数据（密码、令牌等）
- 日志文件权限 600
- 定期轮转和清理

---

## 9. 部署方案

### 9.1 Docker 部署（推荐）

参考 development.md 第 8.1 节。

---

## 10. 开发计划

### 10.1 里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| Phase 1 | 第 1 周 | 基础框架搭建，Python 后端 API，SILK 解码 (SILK→WAV) |
| Phase 2 | 第 2 周 | SILK 编码 (WAV→SILK)，Vue 3 前端界面，多格式支持 |
| Phase 3 | 第 3 周 | PLIST 转换模块，暂存区，日志模块，通知功能 |
| Phase 4 | 第 4 周 | 安全加固，移动端适配，Docker 部署，测试 |
| Phase 5 | 第 5 周 | 数据库音频导入功能，来源标记，完整测试 |

### 10.2 测试用例

**功能测试**
- 单文件 SILK 上传转换
- 多文件批量转换
- 微信 SILK 文件头处理 (0x02)
- 标准 SILK 文件尾处理 (0xffff)
- WAV/MP3 → SILK 编码
- SILK → WAV/MP3 解码
- PLIST 转换与还原
- iOS PLIST 格式验证
- 大文件上传 (接近 50MB 限制)
- 非法格式文件拒绝

**性能测试**
- 并发 5 个转换任务
- 连续转换 50 个文件
- 内存泄漏检测
- 暂存区自动清理

**安全测试**
- 路径遍历攻击
- 文件类型绕过
- XSS 注入测试
- 请求频率限制

---

## 11. 参考资源

| 资源 | 链接 |
|------|------|
| silk-v3-decoder | https://github.com/kn007/silk-v3-decoder |
| silk-v3-encoder | https://github.com/tafayor/silk-codec |
| ffmpeg 文档 | https://ffmpeg.org/documentation.html |
| Vue 3 文档 | https://vuejs.org/ |
| FastAPI 文档 | https://fastapi.tiangolo.com/ |
| Apple PLIST 格式 | https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/PropertyLists/ |

---

## 12. 附录

### 12.1 SILK 编码器命令行参数

```bash
# 使用示例
./silk_v3_encoder input.pcm output.silk [sample_rate] [bit_rate] [frame_size]

# 参数说明
sample_rate: 8000 | 16000 | 24000 (Hz)
bit_rate:    8000 | 12000 | 16000 | 20000 | 24000 | 32000 (bps)
frame_size:  20 | 40 | 60 (ms)

# 示例：24kHz 采样率，24kbps 比特率，20ms 帧大小
./silk_v3_encoder input.pcm output.silk 24000 24000 20
```

### 12.2 SILK 解码器命令行参数

```bash
# 使用示例
./silk_v3_decoder input.silk output.pcm

# 输出为 WAV（需要 ffmpeg 后处理）
./silk_v3_decoder input.silk output.pcm
ffmpeg -f s16le -ar 24000 -ac 1 -i output.pcm output.wav
```

---

## 13. 文档协同与变更流程

### 13.1 文档职责与优先级

1. **职责分工**: PRD.md 定义业务目标、功能范围、验收标准
2. **优先级关系**: development.md > PRD.md > Silk 音频转换器 - UI 设计规范.md
3. **冲突处理**: 当 PRD 示例与技术实现细则冲突时，以 development.md 为准

### 13.2 变更驱动规则

1. **需求变更**: 先更新 PRD.md，再同步 development.md 与 Silk 音频转换器 - UI 设计规范.md
2. **接口变更**: 由 development.md 先定义，再回写 PRD.md 与 Silk 音频转换器 - UI 设计规范.md
3. **视觉调整**: 由 Silk 音频转换器 - UI 设计规范.md 更新，验证不影响 PRD 与 development.md

### 13.3 联动发布检查

- [ ] API 路径与参数风格一致
- [ ] 核心状态枚举一致
- [ ] 上传限制、格式白名单、错误响应语义一致
- [ ] 部署结构与运行命令描述一致
- [ ] 版本号与最后更新日期已同步

---

**本文档定义了完整的产品需求和验收标准。所有开发工作应以此为基准。**
