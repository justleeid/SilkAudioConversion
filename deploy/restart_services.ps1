Param()

# 一键重启脚本（PowerShell），假定放在仓库根目录下
# 功能：停止占用端口的旧进程，启动后端 uvicorn（使用 backend/venv/python 或系统 python），
# 并启动前端静态服务 (python -m http.server 4173)。输出重定向到日志文件。

$ErrorActionPreference = 'Stop'

# 取得脚本所在仓库根路径（脚本放在 deploy 目录下，因此仓库根目录是其上一级）
$DeployDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $DeployDir

$BackendDir = Join-Path $RepoRoot 'backend'
$VenvPython = Join-Path $BackendDir 'venv\Scripts\python.exe'
if (-not (Test-Path $VenvPython)) { $VenvPython = 'python' }

$FrontendDist = Join-Path $RepoRoot 'frontend-v2\dist'

$BackendOut = Join-Path $BackendDir 'backend.out.log'
$BackendErr = Join-Path $BackendDir 'backend.err.log'
$FrontendOut = Join-Path $RepoRoot 'frontend.out.log'
$FrontendErr = Join-Path $RepoRoot 'frontend.err.log'

Write-Host "Repo root: $RepoRoot"
Write-Host "Backend: $BackendDir"

function Stop-ByPort($port) {
    try {
        $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction Stop
        $pid = $conn.OwningProcess
        if ($pid) {
            Write-Host "Stopping process on port $port (PID $pid)"
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } catch {
        Write-Host "No process found on port $port"
    }
}

function Stop-ByCmdMatch($pattern) {
    $matches = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -match $pattern) }
    foreach ($m in $matches) {
        Write-Host "Stopping PID $($m.ProcessId) matching '$pattern'"
        try { Stop-Process -Id $m.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
    }
}

function Remove-Task($taskName) {
    try {
        schtasks /Delete /TN $taskName /F | Out-Null
    } catch {}
}

function Create-And-Run-Task($taskName, $scriptPath) {
    $action = "cmd /c `"$scriptPath`""
    schtasks /Create /TN $taskName /SC ONCE /ST 23:59 /RL HIGHEST /F /TR $action | Out-Null
    schtasks /Run /TN $taskName | Out-Null
}

Write-Host "Stopping existing backend (port 8000 / uvicorn)..."
Stop-ByPort 8000
Stop-ByCmdMatch 'uvicorn'
Stop-ByCmdMatch 'app.main:app'
Remove-Task 'SilkEncodeBackend'

Write-Host "Stopping existing frontend (http.server)..."
Stop-ByCmdMatch 'http.server'
Remove-Task 'SilkEncodeFrontend'

Start-Sleep -Seconds 1

Write-Host "Starting backend using: $VenvPython"
if (-not (Test-Path $BackendDir)) { Write-Host "Warning: $BackendDir not found, please check path" }

$uvicornArgs = @(
    '-m',
    'uvicorn',
    'app.main:app',
    '--host',
    '0.0.0.0',
    '--port',
    '8000',
    '--log-level',
    'info'
)
try {
    Create-And-Run-Task 'SilkEncodeBackend' (Join-Path $DeployDir 'start_backend.cmd')
    Write-Host "Backend scheduled task created and started, log: $BackendOut"
} catch {
    Write-Host "启动 backend 失败: $_"
}

Start-Sleep -Seconds 1

Write-Host "Starting frontend static server (port 4173)..."
if (-not (Test-Path $FrontendDist)) { Write-Host "Warning: $FrontendDist not found, please build frontend first" }

$pythonExe = $VenvPython
$frontendArgs = @(
    '-m',
    'http.server',
    '4173',
    '--bind',
    '0.0.0.0'
)
try {
    Create-And-Run-Task 'SilkEncodeFrontend' (Join-Path $DeployDir 'start_frontend.cmd')
    Write-Host "Frontend scheduled task created and started, log: $FrontendOut"
} catch {
    Write-Host "启动 frontend 失败: $_"
}

Write-Host "Waiting for backend health check..."
$healthy = $false
for ($i=0; $i -lt 15; $i++) {
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $healthy = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}

if ($healthy) { Write-Host "Backend healthy: OK" } else { Write-Host "Backend health check failed; see $BackendOut and $BackendErr" }

Write-Host "Done. Restart script finished. Check logs for details."
