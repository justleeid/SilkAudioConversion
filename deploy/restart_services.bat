@echo off
REM Wrapper to run the PowerShell restart script from Windows Explorer or scheduled tasks
SET SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%restart_services.ps1" %*
