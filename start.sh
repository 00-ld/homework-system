#!/bin/bash
echo "===== 班级作业提交系统 ====="
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q
echo "启动服务: http://localhost:8000"
python main.py
