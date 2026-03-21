Silk 音频格式转换 Web 应用 - 技术规范文档 (Technical Specification v1.1)
1. 文档目的
本文档旨在为开发团队提供明确的技术规范和实现细节，确保：
✅ 使用成熟框架和开源组件，避免重复造轮子
✅ 代码风格统一，便于维护
✅ 所有服务本地部署，不依赖云服务
✅ 防止开发过程中的随意性和技术债务
本文档优先级高于 PRD 文档，开发时必须严格遵守。
2. 技术栈选型（已确认）
2.1 前端技术栈
组件	技术选型	版本	理由
框架	Vue 3	3.4.x	成熟稳定，Composition API
构建工具	Vite	5.x	快速开发，热更新
UI 组件库	Element Plus	2.4.x	成熟中文组件库，移动端支持
语言	TypeScript	5.x	类型安全，减少运行时错误
状态管理	Pinia	2.x	Vue 3 官方推荐，轻量
HTTP 客户端	Axios	1.x	成熟稳定，拦截器支持
文件上传	Element Plus Upload	2.4.x	与 UI 组件库一致，支持拖拽与自定义上传流程
代码规范	ESLint + Prettier	最新	统一代码风格
2.2 后端技术栈
组件	技术选型	版本	理由
框架	FastAPI	0.109.x	高性能，自动文档，类型提示
ASGI 服务器	Uvicorn	0.27.x	轻量高效
虚拟环境	Conda/venv	最新	依赖隔离
文件处理	python-multipart	0.0.6	FastAPI 官方推荐
文件验证	python-magic	0.4.27	文件类型魔数验证
任务队列	asyncio + asyncio.Semaphore	内置	轻量，无需额外服务
日志	loguru	0.7.x	简洁易用，轮转支持
配置管理	pydantic-settings	2.x	类型安全配置
安全	python-jose	3.x	如需扩展认证
2.3 音频处理引擎
组件	技术选型	版本	理由
SILK 解码	silk-v3-decoder	最新	社区维护，MIT 协议
SILK 编码	silk-v3-encoder	最新	配套编码器
音频转换	ffmpeg	6.x	行业标准，格式支持全
PLIST 处理	defusedxml + plistlib	内置	Python 标准库，安全
2.4 部署技术栈
组件	技术选型	版本	理由
容器化	Docker	24.x	环境一致性
编排	Docker Compose	2.x	多服务管理
反向代理	Nginx	1.25.x	高性能，配置简单
进程管理	Supervisor	4.x	非 Docker 部署备选
3. 项目结构规范
3.1 整体目录结构

3.2 Git Submodule 配置

4.1.2 API 调用规范

4.1.3 类型定义规范

4.2 后端编码规范
4.2.1 FastAPI 路由规范

4.2.2 统一响应格式

4.2.3 服务层规范

4.2.4 SILK 文件头处理规范

4.2.5 SILK 编解码服务规范

4.3 日志规范


5. API 设计规范
5.1 RESTful 规范

5.2 统一响应格式

5.3 错误码规范


5.5 转换请求参数约束（补充）
`POST /api/convert` 请求体中，微信兼容模式字段定义如下：

- `wechatCompatible: boolean`，默认 `true`。
- 当 `wechatCompatible=true` 时：输出微信兼容 SILK（添加 `0x02` 头，移除 `b'\xff\xff'` 尾标记）。
- 当 `wechatCompatible=false` 时：输出标准 SILK（不添加 `0x02` 头，保留标准结构）。
6. 安全规范
6.1 文件上传安全

6.2 目录访问控制


6.3 CORS 配置

7.1 环境变量配置

7.2 Python 配置类

8. 部署规范
8.1 Docker 部署（推荐）


8.2 本地开发部署

9. 测试规范
9.1 后端测试

9.2 前端测试
typescript

10. 禁止事项清单
❌ 禁止	✅ 替代方案
手动解析文件头	使用 FileHeaderChecker 类
直接拼接文件路径	使用 get_safe_path() 函数
硬编码配置值	使用 settings 配置类
直接调用 subprocess	封装到 Service 类中
返回原始异常	使用统一响应格式
在前端存储敏感信息	所有敏感数据在后端
使用 eval/exec	使用安全解析库
直接操作文件系统	使用 FileService 封装
忽略日志记录	所有关键操作记录日志
使用云存储/云服务	全部本地存储
11. 开发检查清单
11.1 提交前检查


11.2 代码审查要点
是否使用了成熟组件库
是否有重复造轮子的代码
文件上传是否有完整验证
路径处理是否安全
日志是否完整
配置是否从环境变量读取
错误处理是否统一
类型定义是否完整
12. 附录
12.1 依赖版本锁定

12.2 参考文档
文档	链接
FastAPI 官方文档	https://fastapi.tiangolo.com/
Vue 3 官方文档	https://vuejs.org/
Element Plus 文档	https://element-plus.org/
silk-v3-decoder	https://github.com/kn007/silk-v3-decoder
ffmpeg 文档	https://ffmpeg.org/documentation.html
13. 文档协同与变更流程
13.1 文档优先级




1) 技术规范优先级最高：development.md > PRD.md > ui.md。
2) 任何功能、接口、配置、部署、安全实现，必须先满足本技术规范。
3) PRD.md 负责定义需求边界与业务验收，ui.md 负责定义视觉交互与组件表现。

13.2 跨文档同步规则




1) 当接口结构、字段命名、状态枚举变化时：先更新 development.md，再同步 PRD.md 与 ui.md。
2) 当新增业务能力时：先更新 PRD.md 的需求描述，再补充 development.md 的实现约束，最后更新 ui.md 的交互与状态设计。
3) 当仅视觉风格变化且不影响接口与行为时：更新 ui.md，同时检查 PRD.md 示例图与描述是否仍然一致。

13.3 联动验收清单




- API 路径风格保持一致（路径参数统一使用花括号）
- 统一响应结构保持一致（code/message/data）
- 配置来源保持一致（环境变量 + settings）
- 部署口径保持一致（根目录 docker-compose.yml + backend/frontend 服务）
- UI 展示状态与后端状态枚举一致

13.4 参考关系




1) 需求说明与验收基线：见 PRD.md。
2) 视觉与交互规范：见 ui.md。
3) 若发生冲突，以本技术规范为最终裁决来源。

文档版本: v1.1
创建日期: 2026-03-19
最后更新: 2026-03-19
状态: ✅ 可用于开发指导