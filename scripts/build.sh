#!/bin/bash
set -e
echo "===== 班级作业提交系统 - 构建打包脚本 ====="

echo "[1/3] 安装后端依赖..."
cd backend && pip install -r requirements.txt && cd ..

echo "[2/3] 构建前端..."
cd frontend && npm install && npm run build && cd ..

echo "[3/3] 打包为可执行文件..."
pip install pyinstaller
rm -rf dist/homework_submission_system
pyinstaller homework_submission_system.spec

echo "===== 打包完成 ====="
echo "可执行文件: dist/homework_submission_system/homework_submission_system"
