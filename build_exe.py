"""
班级作业提交系统 - 打包脚本
=======================
运行: python build_exe.py
输出: dist/HomeworkSystem.exe

用法:
  双击 HomeworkSystem.exe 启动服务
  浏览器打开 http://localhost:8000
  手机同一 WiFi 访问局域网地址
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"


def step(msg):
    print(f"\n>>> {msg}")


def check_frontend():
    step("检查前端构建...")
    dist = FRONTEND_DIR / "dist"
    if not (dist / "index.html").exists():
        print("构建前端中...")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)
        subprocess.run(["npm", "run", "build"], cwd=str(FRONTEND_DIR), check=True)
    print("前端已就绪 OK")


def clean_build():
    step("清理旧构建产物...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
    for f in [BASE_DIR / "HomeworkSystem.spec"]:
        if f.exists():
            f.unlink()
    print("已清理 OK")


def build():
    step("开始打包（耗时约 1-2 分钟）...")

    # 前端 dist/ => 打包到 exe 内部的 frontend/dist/
    sep = os.pathsep
    frontend_data = f"{FRONTEND_DIR / 'dist'}{sep}frontend/dist"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name", "HomeworkSystem",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--add-data", frontend_data,
        # uvicorn 动态导入所需
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.middleware.asgi2",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "starlette.middleware.cors",
        "--hidden-import", "multipart",
        str(BASE_DIR / "run.py"),
    ]

    subprocess.run(cmd, check=True, cwd=str(BASE_DIR))
    print("打包完成 OK")


def result():
    exe = DIST_DIR / "HomeworkSystem.exe"
    if exe.exists():
        mb = exe.stat().st_size / (1024 * 1024)
        print(f"""
{'=' * 50}
 打包成功！
{'=' * 50}
  文件: {exe}
  大小: {mb:.1f} MB
{'=' * 50}
  使用方式:
  1. 双击 HomeworkSystem.exe 启动
  2. 浏览器自动打开，用 admin / admin123 登录
  3. 手机连同一 WiFi → 浏览器输入"局域网访问"地址
{'=' * 50}
""")
    else:
        print("打包失败！未生成 exe 文件。")


if __name__ == "__main__":
    os.chdir(str(BASE_DIR))
    check_frontend()
    clean_build()
    build()
    result()
