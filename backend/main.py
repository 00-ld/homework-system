import webbrowser
import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.homework import router as homework_router
from .api.submission import router as submission_router
from .api.student import router as student_router
from .api.feedback import router as feedback_router  # 改进11
from .config import HOST, PORT, FRONTEND_DIST


app = FastAPI(title="班级作业提交系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(homework_router)
app.include_router(submission_router)
app.include_router(student_router)
app.include_router(feedback_router)  # 改进11


def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


@app.on_event("startup")
def seed_defaults():
    from .storage import JsonStore
    s = JsonStore()
    if not s._read_admins():
        s.register_admin("admin", "admin123", "默认班级")
        print("已创建默认管理员: admin / admin123")
    if not s._read_classes():
        s.add_class("默认班级")
        print("已创建默认班级")


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn

    lan_ip = get_lan_ip()

    BANNER = f"""
{'=' * 50}
  班级作业提交系统 v1.0
{'=' * 50}
  本地访问:    http://localhost:{PORT}
  管理后台:    http://localhost:{PORT}/#/admin/login
"""
    if lan_ip:
        BANNER += f"  局域网访问:  http://{lan_ip}:{PORT}\n"
        BANNER += f"  手机访问:  手机连接同一 WiFi，在浏览器输入上方地址\n"
    BANNER += f"{'=' * 50}\n  默认管理员账号: admin / admin123\n{'=' * 50}\n"
    print(BANNER)

    webbrowser.open(f"http://localhost:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
