@echo off
chcp 65001 >nul
REM metro3d node OTA updater (Windows wrapper)
REM usage: deploy-ota.bat [--yes] [--watch] [--interval 30] [--deploy-dir DIR] [--manifest URL] [--notify cmd]
REM logic lives in deploy-ota.ps1 -- this wrapper maps --flag to -Flag
setlocal
set "PSARGS="
:loop
if "%~1"=="" goto run
set "A=%~1"
if /i "%A%"=="--yes"           ( set "PSARGS=%PSARGS% -Yes" & shift & goto loop )
if /i "%A%"=="-y"              ( set "PSARGS=%PSARGS% -Yes" & shift & goto loop )
if /i "%A%"=="--watch"         ( set "PSARGS=%PSARGS% -Watch" & shift & goto loop )
if /i "%A%"=="--interval"      ( set "PSARGS=%PSARGS% -Interval %~2" & shift & shift & goto loop )
if /i "%A%"=="--deploy-dir"    ( set "PSARGS=%PSARGS% -DeployDir ""%~2""" & shift & shift & goto loop )
if /i "%A%"=="--manifest"      ( set "PSARGS=%PSARGS% -Manifest ""%~2""" & shift & shift & goto loop )
if /i "%A%"=="--notify"        ( set "PSARGS=%PSARGS% -Notify ""%~2""" & shift & shift & goto loop )
if /i "%A%"=="--help"          ( powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-ota.ps1" -? & exit /b 0 )
set "PSARGS=%PSARGS% %A%"
shift
goto loop
:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-ota.ps1" %PSARGS%
exit /b %errorlevel%