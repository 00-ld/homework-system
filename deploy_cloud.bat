@echo off
chcp 65001 >nul
title 班级作业提交系统 - 云部署工具
cls

echo =======================================
echo   班级作业提交系统 - 云部署工具
echo   一键部署到 Fly.io（免费，24小时在线）
echo =======================================
echo.

where flyctl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [1/4] 正在安装 flyctl 部署工具...
    echo 请访问 https://fly.io/docs/getting-started/installing-flyctl/
    echo 下载 Windows 版本并安装。
    echo.
    echo 安装后重新运行本脚本即可。
    pause
    exit /b
)

echo [1/4] flyctl 已安装
echo.

echo [2/4] 登录 Fly.io（会打开浏览器）
echo 如果没有账号，按提示注册即可。
echo 需要绑定信用卡验证身份，但不会扣费。
echo 免费额度足够运行本系统。
echo.
pause
call flyctl auth login

echo.
echo [3/4] 初始化应用
call flyctl launch --no-deploy
if %ERRORLEVEL% NEQ 0 (
    echo 初始化失败，请重试。
    pause
    exit /b
)

echo.
echo [4/4] 创建持久化存储卷
call flyctl volumes create data --size 1 --app homework-system
echo.
echo 正在部署...
call flyctl deploy

echo.
echo =======================================
echo  部署完成！
echo  运行以下命令查看访问地址：
echo    flyctl open
echo =======================================
echo  默认管理员: admin / admin123
echo  部署后首次请立即登录修改密码
echo =======================================
pause
