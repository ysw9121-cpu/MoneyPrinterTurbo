@echo off
rem 찐숏폼 일괄 제작: shortform\keywords.txt 의 주제를 한 줄에 한 편씩 만듭니다.
rem 예) shorts.bat --limit 3
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" shorts.py %*
) else if exist "lib\python\python.exe" (
    "lib\python\python.exe" shorts.py %*
) else (
    uv run python shorts.py %*
)
pause
