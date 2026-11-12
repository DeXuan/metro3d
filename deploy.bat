@echo off
REM ============================================================
REM 一键部署（静态托管）
REM 用法：设置环境变量后运行
REM   set DEPLOY_HOST=user@your-server
REM   set DEPLOY_DIR=/var/www/metro3d
REM   deploy.bat
REM ============================================================
setlocal

if "%DEPLOY_HOST%"=="" (
  echo [错误] 请先设置 DEPLOY_HOST，如: set DEPLOY_HOST=user@server.example.com
  exit /b 1
)
if "%DEPLOY_DIR%"=="" (
  echo [错误] 请先设置 DEPLOY_DIR，如: set DEPLOY_DIR=/var/www/metro3d
  exit /b 1
)

if not exist "index.html" (
  echo [错误] 找不到 index.html，请在本项目目录下执行
  exit /b 1
)

echo ==^> [1/3] 确保远端目录存在
ssh %DEPLOY_HOST% "mkdir -p %DEPLOY_DIR%"

echo ==^> [2/3] 备份远端旧版
ssh %DEPLOY_HOST% "cp -f %DEPLOY_DIR%/index.html %DEPLOY_DIR%/index.html.bak-$(date +%%Y%%m%%d-%%H%%M%%S) 2>/dev/null || true"

echo ==^> [3/3] 上传 index.html
scp index.html %DEPLOY_HOST%:%DEPLOY_DIR%/

echo ✅ 部署完成
endlocal
