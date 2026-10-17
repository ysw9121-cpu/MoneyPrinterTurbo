@echo off
chcp 65001 >nul
rem 무인 실행용 shorts.bat: 창을 멈추지 않고 결과를 shortform\auto-run.log 에 남깁니다.
rem 작업 스케줄러가 이 파일을 실행합니다. 예) shorts_auto.bat --limit 3
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
set "PYTHONIOENCODING=utf-8"
set "LOG_FILE=shortform\auto-run.log"
echo ===== %DATE% %TIME% ===== >> "%LOG_FILE%"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" shorts.py %* >> "%LOG_FILE%" 2>&1
) else if exist "lib\python\python.exe" (
    "lib\python\python.exe" shorts.py %* >> "%LOG_FILE%" 2>&1
) else (
    uv run python shorts.py %* >> "%LOG_FILE%" 2>&1
)
