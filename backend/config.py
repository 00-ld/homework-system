import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # PyInstaller 打包后：数据目录在 exe 旁边，前端在 _internal 中
    BASE_DIR = Path(sys.executable).parent
    _INTERNAL_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    _INTERNAL_DIR = BASE_DIR

DATA_DIR = Path(os.environ.get("HOMEWORK_DATA_DIR", BASE_DIR / "data"))
FRONTEND_DIST = _INTERNAL_DIR / "frontend" / "dist"

ADMIN_PASSWORD = "admin123"
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

for d in [DATA_DIR, DATA_DIR / "uploads"]:
    os.makedirs(d, exist_ok=True)
