@echo off
cd /d D:\repository\silk_encode\frontend-v2\dist
D:\repository\silk_encode\backend\venv\Scripts\python.exe -m http.server 4173 --bind 0.0.0.0 >> D:\repository\silk_encode\frontend.out.log 2>> D:\repository\silk_encode\frontend.err.log
exit /b %errorlevel%
