部署目录 deploy 下包含一键重启脚本：

- 文件: deploy/restart_services.ps1
- 包装: deploy/restart_services.bat

用法（在远端 Windows 服务器 D:\repository\silk_encode 路径下运行）：

PowerShell (推荐，管理员或允许执行策略)：

    powershell -NoProfile -ExecutionPolicy Bypass -File deploy\restart_services.ps1

或双击批处理文件：

    deploy\restart_services.bat

说明：
- 脚本假定放在仓库根目录（脚本会基于自身位置查找 `backend` 与 `frontend-v2/dist`）。
- 后端使用 `backend/venv/Scripts/python.exe`（若存在），否则使用系统 `python`。
- 后端监听端口: 8000；前端静态服务端口: 4173。
- 日志输出到 `backend/backend.out.log`、`backend/backend.err.log`、`frontend.out.log`、`frontend.err.log`。
- 若需将后端注册为 Windows 服务或做开机自启，请使用 nssm 或 Windows 服务管理工具。
