@echo off
chcp 65001 >nul
rem 매일 정해진 시각에 숏폼을 자동으로 만들도록 윈도우 작업 스케줄러에 등록합니다.
rem   schedule_shorts.bat              매일 09:00에 3편
rem   schedule_shorts.bat 20:30 5      매일 20:30에 5편
rem   schedule_shorts.bat off          자동 제작 해제
setlocal
set "TASK_NAME=JjinShorts"
if /i "%~1"=="off" (
    schtasks /Delete /TN "%TASK_NAME%" /F
) else (
    set "RUN_AT=%~1"
    set "LIMIT=%~2"
    call :register
)
pause
exit /b

:register
if "%RUN_AT%"=="" set "RUN_AT=09:00"
if "%LIMIT%"=="" set "LIMIT=3"
schtasks /Create /F /SC DAILY /ST %RUN_AT% /TN "%TASK_NAME%" /TR "\"%~dp0shorts_auto.bat\" --limit %LIMIT%"
if errorlevel 1 (
    echo 등록에 실패했습니다. 시각은 09:00 처럼 24시간 형식으로 적어주세요.
) else (
    echo 매일 %RUN_AT%에 숏폼 %LIMIT%편을 자동으로 만듭니다.
    echo 결과는 shortform\auto-run.log 와 shortform\done.txt 에서 확인하세요.
    echo 해제하려면: schedule_shorts.bat off
)
exit /b
