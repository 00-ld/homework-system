@echo off
chcp 65001 >nul
title 班级作业提交系统
echo ========================================
echo  班级作业提交系统 正在启动...
echo ========================================

cd /d "%~dp0"

cd backend

echo 安装依赖...
pip install -r requirements.txt >nul 2>&1

echo.
echo 启动服务...
echo 管理后台: http://localhost:8000/#/admin/login
echo ========================================
echo.

python main.py
pause
