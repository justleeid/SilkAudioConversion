📋 Silk 音频格式转换 Web 应用 - 产品需求文档 (PRD v3.2)
1. 项目概述
1.1 项目背景
微信、Skype、QQ 等通讯软件使用 SILK 音频编码格式，该格式无法在常规播放器中播放。现有的 silk-v3-decoder 项目仅支持客户端命令行方式运行，缺乏 Web 界面。本项目旨在构建一个前后端分离的 Web 应用，实现 SILK 格式与其他音频格式的双向转换。
1.2 项目目标
目标	描述
核心功能	实现 SILK ↔ WAV/MP3 双向转换
用户体验	提供简洁的 Web 界面，支持移动端访问
部署方式	局域网部署，无需外网依赖，无需登录
安全要求	基础安全配置，文件访问控制，可配置日志
特殊场景	支持 iOS 预定义语音打包为 PLIST
1.3 技术选型（已确认）




前端：Vue 3 + Vite + TypeScript + Element Plus
后端：Python (FastAPI) + Anaconda/venv 虚拟环境
音频处理：silk-v3-decoder + silk-v3-encoder + ffmpeg
存储：本地文件系统 + 临时存储区
部署：Docker 或直接部署 + Nginx 反向代理

说明：当 PRD 与技术规范存在冲突时，以 development.md 为准。
2. 功能需求
2.1 核心功能模块
2.1.1 音频上传模块
功能项	详细描述	优先级
单文件上传	支持拖拽或点击选择单个音频文件	P0
多文件上传	支持批量选择多个文件（建议上限 50 个）	P0
格式检测	自动识别上传文件格式（silk/wav/mp3/amr 等）	P0
大小限制	可配置上传大小限制（默认 50MB/文件）	P0
格式限制	仅允许指定格式上传，拒绝非法文件	P0
2.1.2 SILK 转普通格式（解码）
功能项	详细描述	优先级
SILK → WAV	转换为标准 WAV 格式（16bit PCM）	P0
SILK → MP3	转换为 MP3 格式（可配置比特率）	P0
微信头处理	自动检测并处理 0x02 文件头字节	P0
结尾处理	检测并处理 b'\xff\xff' 结尾标记	P0
批量转换	支持多文件队列转换	P1
2.1.3 普通格式转 SILK（编码）
功能项	详细描述	优先级
WAV → SILK	转换为微信兼容的 SILK 格式	P0
MP3 → SILK	转换为微信兼容的 SILK 格式	P0
采样率配置	支持 8kHz/16kHz/24kHz 采样率选择	P0
比特率配置	支持 SILK 编码比特率配置	P2
微信头添加	转换后自动添加 0x02 文件头，移除 b'\xff\xff'	P0
帧大小配置	支持 20ms/40ms/60ms 帧大小选择	P2
微信兼容模式开关	保留可选开关：开启输出微信兼容 SILK；关闭输出标准 SILK	P0
2.1.4 PLIST 转换模块（iOS 预定义语音）
功能项	详细描述	优先级
SILK → PLIST	将 SILK 文件转为 Apple XML plist 格式	P1
多文件合并	多个 SILK 合并为一个 plist 文件	P1
PLIST → SILK	从 plist 还原为原始 SILK 文件	P1
格式规范	<key>文件名</key><string>base64 内容</string>	P1
iOS 兼容	符合 iOS NSBundle 资源加载规范	P1
元数据支持	可选添加 duration、sampleRate 等元数据	P2
2.1.5 暂存区模块
功能项	详细描述	优先级
临时存储	转换结果暂存 48 小时（可配置）	P1
下载链接	生成唯一下载链接	P1
跨端访问	同一局域网内其他设备可下载	P1
自动清理	定时清理过期文件	P1
2.1.6 通知模块
功能项	详细描述	优先级
转换完成通知	前端弹窗/消息提示	P1
进度显示	实时显示转换进度百分比	P1
错误通知	转换失败时显示错误原因	P1
2.1.7 日志模块
功能项	详细描述	优先级
日志开关	可配置开启/关闭日志记录	P1
日志级别	支持 INFO/WARNING/ERROR 等级别	P1
日志内容	记录上传、转换、下载等操作	P1
日志存储	本地文件存储，可配置轮转策略	P1
3. SILK 格式技术细节（已确认）
3.1 文件头结构对比




┌─────────────────────────────────────────────────────────────────┐
│                    标准 SILK 文件格式                            │
├─────────────────────────────────────────────────────────────────┤
│  开头: b'#!silk_v3' (9 字节)                                     │
│  结尾: b'\xff\xff' (2 字节)                                      │
│  内容: SILK 编码音频数据                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    微信 SILK 文件格式                            │
├─────────────────────────────────────────────────────────────────┤
│  开头: b'\x02' + b'#!silk_v3' (10 字节)                          │
│  结尾: 无 b'\xff\xff' 标记                                       │
│  内容: SILK 编码音频数据                                          │
└─────────────────────────────────────────────────────────────────┘
3.2 编码/解码处理流程
python




# ============================================
# SILK 解码流程（微信 SILK → WAV/MP3）
# ============================================
def decode_wechat_silk(input_file, output_file, output_format='wav'):
    """
    SILK 解码为 WAV/MP3
    """
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
    # 命令：./silk_v3_decoder input.silk output.pcm
    pcm_file = run_decoder(temp_silk)
    
    # 6. 使用 ffmpeg 转换为 WAV/MP3
    # 命令：ffmpeg -f s16le -ar 24000 -ac 1 -i input.pcm output.wav
    ffmpeg_convert(pcm_file, output_file, output_format)
    
    return output_file

# ============================================
# SILK 编码流程（WAV/MP3 → 微信 SILK）
# ============================================
def encode_wechat_silk(input_file, output_file, sample_rate=24000, 
                       bit_rate=24000, frame_size=20):
    """
    WAV/MP3 编码为微信兼容 SILK
    """
    # 1. 使用 ffmpeg 转换为 PCM（16bit 单声道）
    # 命令：ffmpeg -i input.wav -f s16le -acodec pcm_s16le -ar 24000 -ac 1 output.pcm
    pcm_file = ffmpeg_to_pcm(input_file, sample_rate)
    
    # 2. 使用 silk-v3-encoder 编码为 SILK
    # 命令：./silk_v3_encoder input.pcm output.silk 24000 24000 20
    # 参数：采样率 比特率 帧大小 (ms)
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
3.3 采样率与场景对照表
采样率	比特率	帧大小	适用场景	文件大小	音质
8 kHz	8-12 kbps	20ms	语音通话，最低带宽	最小	一般
16 kHz	16-20 kbps	20ms	微信语音默认	中等	良好
24 kHz	24-32 kbps	20ms	高质量语音，iOS 预定义	最大	优秀
3.4 PLIST 格式规范（iOS 预定义语音）
转换生成后的单文件示例
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>voice_001.silk</key>
    <string>base64_encoded_content_1</string>
</dict>
</plist>

转换生成后的多文件转换示例
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>voice_001.silk</key>
    <string>base64_encoded_content_1</string>
    <key>voice_002.silk</key>
    <string>base64_encoded_content_1</string>
    <key>voice_003.silk</key>
    <string>base64_encoded_content_1</string>
    <key>voice_004.silk</key>
    <string>base64_encoded_content_1</string>
</dict>
</plist>

iOS 使用示例：

4. 技术架构
4.1 系统架构图




┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ 文件上传  │  │ 转换配置  │  │ 进度展示  │  │ 结果下载  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                    后端 (Python FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ 文件接收  │  │ 格式检测  │  │ 转换调度  │  │ 临时存储  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ 日志模块  │  │ 配置管理  │  │ 任务队列  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              ↓ 子进程调用
┌─────────────────────────────────────────────────────────────┐
│                    音频处理引擎                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ silk-v3-decoder  │  │  silk-v3-encoder │                │
│  │ (SILK → PCM)     │  │  (PCM → SILK)    │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────────────────────────────┐              │
│  │              ffmpeg                      │              │
│  │  (PCM ↔ MP3/WAV, WAV/MP3 → PCM)          │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
4.2 目录结构

5. API 接口设计
5.1 上传接口



5.2 转换接口



5.3 查询转换状态



5.4 下载接口


5.5 PLIST 专用接口


5.6 文件管理接口


5.7 配置接口


6. 配置管理
6.1 环境变量配置 (.env)


7. 前端页面设计
7.1 页面结构




┌─────────────────────────────────────────────────────────────┐
│  🎵 Silk 音频转换器                      [设置] [关于]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              📤 拖拽文件到此处或点击上传              │   │
│  │           支持 .silk .wav .mp3 .amr                 │   │
│  │               单文件最大 50MB                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  已选择文件 (3):                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📄 voice_001.silk    1.2MB    24kHz    [×]          │   │
│  │ 📄 voice_002.silk    0.8MB    16kHz    [×]          │   │
│  │ 📄 voice_003.silk    1.5MB    24kHz    [×]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  转换设置:                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 目标格式：○ WAV  ○ MP3  ○ SILK  ○ PLIST            │   │
│  │                                                     │   │
│  │ [SILK 输出选项]                                     │   │
│  │ 采样率：  [24 kHz ▼]                                │   │
│  │ 比特率：  [24 kbps ▼]                               │   │
│  │ 帧大小：  [20 ms ▼]                                 │   │
│  │ □ 微信兼容模式 (添加 0x02 文件头)                     │   │
│  │                                                     │   │
│  │ [PLIST 输出选项]                                    │   │
│  │ 文件名：  [voices    ]                              │   │
│  │ □ 包含元数据 (duration, sampleRate)                  │   │
│  │ □ 合并为单个文件                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [开始转换]                          [清空列表]             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  转换任务:                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✅ voice_001.wav    2.1MB    [下载] [删除]          │   │
│  │ ⏳ voice_002.wav    ████████░░ 80%   预计 2 秒       │   │
│  │ ⏳ voice_003.wav    ████░░░░░░ 40%   预计 5 秒       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  暂存区: 10 个文件 | 已用 125MB | 48 小时后自动清理          │
│  [查看暂存区] [立即清理过期文件]                            │
└─────────────────────────────────────────────────────────────┘
7.2 移动端适配

8. 安全配置
8.1 服务端安全
python




# 文件上传安全中间件

8.2 日志安全
python





9. 部署方案
9.1 Docker 部署 (推荐)

10. 开发计划
10.1 里程碑
阶段	时间	交付物
Phase 1	第 1 周	基础框架搭建，Python 后端 API，SILK 解码 (SILK→WAV)
Phase 2	第 2 周	SILK 编码 (WAV→SILK)，Vue 3 前端界面，多格式支持
Phase 3	第 3 周	PLIST 转换模块，暂存区，日志模块，通知功能
Phase 4	第 4 周	安全加固，移动端适配，Docker 部署，测试
10.2 测试用例
yaml




功能测试:
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

性能测试:
  - 并发 5 个转换任务
  - 连续转换 50 个文件
  - 内存泄漏检测
  - 暂存区自动清理

安全测试:
  - 路径遍历攻击
  - 文件类型绕过
  - XSS 注入测试
  - 请求频率限制
11. 参考资源
资源	链接
silk-v3-decoder	https://github.com/kn007/silk-v3-decoder
silk-v3-encoder	https://github.com/tafayor/silk-codec
ffmpeg 文档	https://ffmpeg.org/documentation.html
Vue 3 文档	https://vuejs.org/
FastAPI 文档	https://fastapi.tiangolo.com/
Apple PLIST 格式	https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/PropertyLists/
12. 附录
12.1 SILK 编码器命令行参数
bash




# silk_v3_encoder 使用示例
./silk_v3_encoder input.pcm output.silk [sample_rate] [bit_rate] [frame_size]

# 参数说明
sample_rate: 8000 | 16000 | 24000 (Hz)
bit_rate:    8000 | 12000 | 16000 | 20000 | 24000 | 32000 (bps)
frame_size:  20 | 40 | 60 (ms)

# 示例：24kHz 采样率，24kbps 比特率，20ms 帧大小
./silk_v3_encoder input.pcm output.silk 24000 24000 20
12.2 SILK 解码器命令行参数
bash




# silk_v3_decoder 使用示例
./silk_v3_decoder input.silk output.pcm

# 输出为 WAV（需要 ffmpeg 后处理）
./silk_v3_decoder input.silk output.pcm
ffmpeg -f s16le -ar 24000 -ac 1 -i output.pcm output.wav

  13. 文档协同与变更流程
  13.1 文档职责与优先级




  1) 职责分工：PRD.md 定义业务目标、功能范围、验收标准。
  2) 优先级关系：development.md > PRD.md > ui.md。
  3) 当 PRD 示例与技术实现细则冲突时，以 development.md 为准；当视觉交互描述冲突时，以 ui.md 的实现规范为准但不得突破技术约束。

  13.2 变更驱动规则




  1) 需求新增/删除/优先级变更：先更新 PRD.md，再同步 development.md 与 ui.md。
  2) 接口字段或状态变更：由 development.md 先定义，再回写 PRD.md 接口章节与 ui.md 状态展示。
  3) 纯视觉调整：由 ui.md 更新，但需验证不影响 PRD 业务流程与 development.md 技术边界。

  13.3 联动发布检查




  - 三份文档中的 API 路径与参数风格一致
  - 三份文档中的核心状态枚举一致
  - 上传限制、格式白名单、错误响应语义一致
  - 部署结构与运行命令描述一致
  - 版本号与最后更新日期已同步

    文档版本: v3.2
创建日期: 2026-03-19
最后更新: 2026-03-19
状态: ✅ 已完成，可用于开发