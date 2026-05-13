"""班级作业提交系统 - 启动入口"""
import os
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中（让 backend.xxx 可导入）
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(str(BASE_DIR))

def _get_lan_ip() -> str:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


if __name__ == "__main__":
    from backend.main import app
    from backend.config import HOST, PORT
    import uvicorn

    lan_ip = _get_lan_ip()
    BANNER = f"""
{'=' * 50}
  班级作业提交系统 v1.0
{'=' * 50}
  本地访问:    http://localhost:{PORT}
  管理后台:    http://localhost:{PORT}/#/admin/login
"""
    if lan_ip:
        BANNER += f"  局域网访问:  http://{lan_ip}:{PORT}\n"
        BANNER += "  手机访问:  手机连接同一 WiFi，在浏览器输入上方地址\n"
    BANNER += f"{'=' * 50}\n  默认管理员账号: admin / admin123\n{'=' * 50}\n"
    print(BANNER)

    import webbrowser
    webbrowser.open(f"http://localhost:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
