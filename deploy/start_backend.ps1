$ErrorActionPreference = 'Stop'
Set-Location 'D:\repository\silk_encode\backend'
& 'D:\repository\silk_encode\backend\venv\Scripts\python.exe' -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info 1>> 'D:\repository\silk_encode\backend\backend.out.log' 2>> 'D:\repository\silk_encode\backend\backend.err.log'
