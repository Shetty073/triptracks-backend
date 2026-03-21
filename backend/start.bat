@echo off
setlocal

if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8001
if "%WORKERS%"=="" set WORKERS=4
if "%LOG_LEVEL%"=="" set LOG_LEVEL=info

echo Starting Triptracks API (Production Setup)...
echo =^> Host: %HOST%
echo =^> Port: %PORT%
echo =^> Workers: %WORKERS%
echo =^> Log Level: %LOG_LEVEL%

if exist "venv\" (
    echo =^> Activating virtual environment...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    ) else (
        echo WARNING: Could not find activate script in venv.
    )
) else (
    echo WARNING: No virtual environment found at .\venv. Assuming dependencies are globally installed.
)

uvicorn app.main:app ^
    --host %HOST% ^
    --port %PORT% ^
    --workers %WORKERS% ^
    --log-level %LOG_LEVEL% ^
    --proxy-headers ^
    --forwarded-allow-ips="*" ^
    --timeout-keep-alive 65
