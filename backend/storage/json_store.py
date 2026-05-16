import json
import os
import shutil
import zipfile
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..config import DATA_DIR


class JsonStore:
    # 改进: 共享 token 存储（跨模块实例共享）
    _tokens: dict[str, str] = {}

    def __init__(self):
        self.homeworks_file = DATA_DIR / "homeworks.json"
        self.students_file = DATA_DIR / "students.json"
        self.admins_file = DATA_DIR / "admins.json"
        self.classes_file = DATA_DIR / "classes.json"
        self.email_config_file = DATA_DIR / "email_config.json"
        self.feedbacks_file = DATA_DIR / "feedbacks.json"  # 改进11: 反馈存储
        self.uploads_dir = DATA_DIR / "uploads"
        # 云部署时使用 PostgreSQL 持久化数据
        self._use_db = bool(os.environ.get("DATABASE_URL"))
        if self._use_db:
            from .db_store import init_db
            init_db()
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(self.uploads_dir, exist_ok=True)
        if self._use_db:
            return  # 数据库模式不需要初始化文件
        if not self.homeworks_file.exists():
            self._write_json([])
        if not self.students_file.exists():
            self._write_students([])
        if not self.admins_file.exists():
            self._write_admins([])
        if not self.classes_file.exists():
            self._write_classes([])
        if not self.email_config_file.exists():
            self._write_email_config({})
        if not self.feedbacks_file.exists():  # 改进11: 初始化反馈文件
            self._write_feedbacks([])

    def _read_json(self) -> list:
        if self._use_db:
            from .db_store import read_homeworks
            return read_homeworks()
        try:
            with open(self.homeworks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_json(self, data: list):
        if self._use_db:
            from .db_store import write_homeworks
            write_homeworks(data)
            return
        with open(self.homeworks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _read_students(self) -> list:
        if self._use_db:
            from .db_store import read_students
            return read_students()
        try:
            with open(self.students_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_students(self, data: list):
        if self._use_db:
            from .db_store import write_students
            write_students(data)
            return
        with open(self.students_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _read_admins(self) -> list:
        if self._use_db:
            from .db_store import read_admins
            return read_admins()
        try:
            with open(self.admins_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_admins(self, data: list):
        if self._use_db:
            from .db_store import write_admins
            write_admins(data)
            return
        with open(self.admins_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _read_classes(self) -> list:
        if self._use_db:
            from .db_store import read_classes
            return read_classes()
        try:
            with open(self.classes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_classes(self, data: list):
        if self._use_db:
            from .db_store import write_classes
            write_classes(data)
            return
        with open(self.classes_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --- Admin methods ---

    def register_admin(self, username: str, password: str, class_name: str) -> dict:
        admins = self._read_admins()
        for a in admins:
            if a["username"] == username:
                return {"error": "duplicate", "message": "用户名已存在"}
        admin = {"username": username, "password": password, "class_name": class_name, "created_at": datetime.now().isoformat()}
        admins.append(admin)
        self._write_admins(admins)
        return admin

    def verify_admin(self, username: str, password: str) -> Optional[dict]:
        admins = self._read_admins()
        for a in admins:
            if a["username"] == username and a["password"] == password:
                return a
        return None

    def create_token(self, username: str) -> str:
        token = str(uuid.uuid4())
        self._tokens[token] = username
        return token

    def get_admin_by_token(self, token: str) -> Optional[dict]:
        username = self._tokens.get(token)
        if not username:
            return None
        admins = self._read_admins()
        for a in admins:
            if a["username"] == username:
                return a
        return None

    def list_all_admins(self) -> list:
        return self._read_admins()

    def delete_admin(self, username: str) -> bool:
        admins = self._read_admins()
        for i, a in enumerate(admins):
            if a["username"] == username:
                admins.pop(i)
                self._write_admins(admins)
                return True
        return False

    def list_students_by_class(self, class_name: str, active_only: bool = True) -> list:
        students = self._read_students()
        result = [s for s in students if s.get("class_name") == class_name]
        if active_only:
            result = [s for s in result if s.get("status", "active") == "active"]
        return result

    # 改进5: 返回所有学生（包括非活跃的）
    def list_all_students(self) -> list:
        return self._read_students()

    # 改进5: 标记学生为非活跃
    def deactivate_student(self, student_id: str) -> bool:
        students = self._read_students()
        for s in students:
            if s["student_id"] == student_id:
                s["status"] = "inactive"
                s["deactivated_at"] = datetime.now().isoformat()
                self._write_students(students)
                return True
        return False

    # 改进5: 重新激活学生
    def activate_student(self, student_id: str) -> bool:
        students = self._read_students()
        for s in students:
            if s["student_id"] == student_id:
                s["status"] = "active"
                s["activated_at"] = datetime.now().isoformat()
                self._write_students(students)
                return True
        return False

    # --- Class methods ---

    def list_classes(self) -> list:
        return self._read_classes()

    def add_class(self, name: str) -> dict:
        classes = self._read_classes()
        if name in classes:
            return {"error": "duplicate", "message": "班级已存在"}
        classes.append(name)
        self._write_classes(classes)
        return {"name": name}

    # --- Homework with class filter ---

    def list_homeworks_by_class(self, class_name: str) -> list:
        all_hw = self._read_json()
        return [h for h in all_hw if h.get("class_name") == class_name]

    # --- Student with class ---

    def _read_email_config(self) -> dict:
        if self._use_db:
            from .db_store import read_email_config
            return read_email_config()
        try:
            with open(self.email_config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_email_config(self, data: dict):
        if self._use_db:
            from .db_store import write_email_config
            write_email_config(data)
            return
        with open(self.email_config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_email_config(self) -> dict:
        return self._read_email_config()

    def save_email_config(self, config: dict) -> dict:
        self._write_email_config(config)
        return config

    def find_all_phones_by_homework(self, hw_id: str) -> list[dict]:
        """返回所有提交了该作业且有联系方式的学生 [{name, id, phone, email}]"""
        hw = self.get_homework(hw_id)
        if not hw:
            return []
        students = self._read_students()
        submitted_ids = {s["student_id"] for s in hw.get("submissions", [])}
        result = []
        for s in students:
            if s["student_id"] in submitted_ids and (s.get("phone") or s.get("email")):
                result.append(s)
        return result

    def _find_homework(self, homeworks: list, hw_id: str) -> Optional[dict]:
        for hw in homeworks:
            if hw["id"] == hw_id:
                return hw
        return None

    def create_homework(self, title: str, description: str, due_date: str, allow_resubmit: bool = False, class_name: str = "") -> dict:
        homeworks = self._read_json()
        now = datetime.now().isoformat()
        hw = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "due_date": due_date,
            "created_at": now,
            "link_id": str(uuid.uuid4()).replace("-", ""),
            "allow_resubmit": allow_resubmit,
            "class_name": class_name,
            "submissions": []
        }
        homeworks.insert(0, hw)
        self._write_json(homeworks)
        return hw

    def list_homeworks(self) -> list:
        return self._read_json()

    def get_homework(self, hw_id: str) -> Optional[dict]:
        homeworks = self._read_json()
        return self._find_homework(homeworks, hw_id)

    def get_homework_by_link(self, link_id: str) -> Optional[dict]:
        homeworks = self._read_json()
        for hw in homeworks:
            if hw["link_id"] == link_id:
                return hw
        return None

    def delete_homework(self, hw_id: str) -> bool:
        homeworks = self._read_json()
        hw = self._find_homework(homeworks, hw_id)
        if not hw:
            return False
        hw_dir = self.uploads_dir / self._sanitize_path_component(f"{hw['due_date']}_{hw['title']}")
        if hw_dir.exists():
            shutil.rmtree(hw_dir)
        homeworks = [h for h in homeworks if h["id"] != hw_id]
        self._write_json(homeworks)
        return True

    def save_submission(self, link_id: str, student_name: str, student_id: str, files: list[str], total_size: int) -> Optional[dict]:
        homeworks = self._read_json()
        hw = None
        for h in homeworks:
            if h["link_id"] == link_id:
                hw = h
                break
        if not hw:
            return None
        subs = hw.setdefault("submissions", [])
        for i, sub in enumerate(subs):
            if sub["student_id"] == student_id:
                subs.pop(i)
                break
        sub = {
            "student_name": student_name,
            "student_id": student_id,
            "files": files,
            "submitted_at": datetime.now().isoformat(),
            "file_size": total_size
        }
        subs.append(sub)
        self._write_json(homeworks)
        return sub

    def check_submission(self, link_id: str, student_name: str, student_id: str) -> Optional[dict]:
        homeworks = self._read_json()
        for h in homeworks:
            if h["link_id"] == link_id:
                for sub in h.get("submissions", []):
                    if sub["student_id"] == student_id:
                        return sub
                return None
        return None

    @staticmethod
    def _sanitize_path_component(name: str) -> str:
        """Windows 安全：移除文件名中不允许的字符"""
        invalid_chars = '<>:"/\\|?*'
        for c in invalid_chars:
            name = name.replace(c, '_')
        return name.strip()[:200]  # 限制长度，避免路径过长

    def get_submission_dir(self, hw: dict, student_name: str, student_id: str) -> Path:
        dir_name = self._sanitize_path_component(f"{hw['due_date']}_{hw['title']}")
        student_dir = self.uploads_dir / dir_name / self._sanitize_path_component(f"{student_name}_{student_id}")
        os.makedirs(student_dir, exist_ok=True)
        return student_dir

    # 改进5: 保留所有人历史注册信息 — 学号重复时更新而非拒绝
    def register_student(self, student_name: str, student_id: str, phone: str = "", class_name: str = "", email: str = "") -> dict:
        students = self._read_students()
        for s in students:
            if s["student_id"] == student_id:
                # 学号已存在，更新信息但保留原记录
                old_name = s.get("student_name")
                s["student_name"] = student_name
                if phone:
                    s["phone"] = phone
                if email:
                    s["email"] = email
                if class_name:
                    s["class_name"] = class_name
                s["status"] = "active"
                s["updated_at"] = datetime.now().isoformat()
                # 记录历史名称变化
                history = s.setdefault("history", [])
                if old_name and old_name != student_name:
                    history.append({"field": "student_name", "from": old_name, "to": student_name, "changed_at": datetime.now().isoformat()})
                self._write_students(students)
                return {"message": "信息已更新", "student": s, "updated": True}
        student = {
            "student_name": student_name,
            "student_id": student_id,
            "phone": phone,
            "email": email,
            "class_name": class_name,
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        students.append(student)
        self._write_students(students)
        return student

    def update_student_phone(self, student_id: str, phone: str) -> Optional[dict]:
        students = self._read_students()
        for s in students:
            if s["student_id"] == student_id:
                s["phone"] = phone
                self._write_students(students)
                return s
        return None

    def verify_student(self, student_id: str, student_name: str) -> Optional[dict]:
        students = self._read_students()
        for s in students:
            if s["student_id"] == student_id and s["student_name"] == student_name:
                return s
        return None

    def get_student_by_id(self, student_id: str) -> Optional[dict]:
        students = self._read_students()
        for s in students:
            if s["student_id"] == student_id:
                return s
        return None

    def list_students(self) -> list:
        return self._read_students()

    def export_csv(self, hw_id: str) -> Optional[str]:
        hw = self.get_homework(hw_id)
        if not hw:
            return None
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["姓名", "学号", "提交时间", "文件列表", "文件大小(B)"])
        for sub in hw.get("submissions", []):
            writer.writerow([
                sub["student_name"],
                sub["student_id"],
                sub["submitted_at"],
                "; ".join(sub["files"]),
                sub["file_size"]
            ])
        return output.getvalue()

    # ─── 改进11: 意见与Bug反馈系统 ───

    def _read_feedbacks(self) -> list:
        if self._use_db:
            from .db_store import read_feedbacks
            return read_feedbacks()
        try:
            with open(self.feedbacks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_feedbacks(self, data: list):
        if self._use_db:
            from .db_store import write_feedbacks
            write_feedbacks(data)
            return
        with open(self.feedbacks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_feedback(self, name: str, contact: str, content: str, feedback_type: str) -> dict:
        feedbacks = self._read_feedbacks()
        fb = {
            "id": str(uuid.uuid4()),
            "name": name,
            "contact": contact,
            "content": content,
            "type": feedback_type,
            "created_at": datetime.now().isoformat()
        }
        feedbacks.insert(0, fb)
        self._write_feedbacks(feedbacks)
        return fb

    def list_feedbacks(self, page: int = 1, page_size: int = 20) -> dict:
        feedbacks = self._read_feedbacks()
        total = len(feedbacks)
        start = (page - 1) * page_size
        end = start + page_size
        items = feedbacks[start:end]
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_feedback_stats(self) -> dict:
        feedbacks = self._read_feedbacks()
        total = len(feedbacks)
        by_type = {}
        for fb in feedbacks:
            t = fb.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        return {"total": total, "by_type": by_type}

    def delete_feedback(self, fb_id: str) -> bool:
        feedbacks = self._read_feedbacks()
        for i, fb in enumerate(feedbacks):
            if fb["id"] == fb_id:
                feedbacks.pop(i)
                self._write_feedbacks(feedbacks)
                return True
        return False

    # 改进13: 导出文件命名修复 — 完全保留原始文件名
    # 大文件优化: 使用临时文件避免内存溢出，返回生成器
    def create_submission_zip(self, hw_id: str, flat: bool = False) -> Optional[bytes]:
        hw = self.get_homework(hw_id)
        if not hw:
            return None
        dir_name = self._sanitize_path_component(f"{hw['due_date']}_{hw['title']}")
        hw_dir = self.uploads_dir / dir_name
        if not hw_dir.exists():
            return None
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for student_dir in hw_dir.iterdir():
                if student_dir.is_dir():
                    for file_path in student_dir.rglob("*"):
                        if file_path.is_file():
                            if flat:
                                arcname = file_path.name
                            else:
                                # 改进13: 确保路径为 {student_name}_{student_id}/{original_filename}
                                arcname = f"{student_dir.name}/{file_path.name}"
                            zf.write(file_path, arcname)
        buf.seek(0)
        return buf.getvalue()

    # 大文件优化: 生成器方式分块读取 ZIP 文件, 用于 StreamingResponse
    def iter_submission_zip_chunks(self, hw_id: str, flat: bool = False, chunk_size: int = 8 * 1024 * 1024):
        """生成 ZIP 文件的分块数据，用于 StreamingResponse"""
        hw = self.get_homework(hw_id)
        if not hw:
            return
        dir_name = self._sanitize_path_component(f"{hw['due_date']}_{hw['title']}")
        hw_dir = self.uploads_dir / dir_name
        if not hw_dir.exists():
            return
        import tempfile
        import io
        # 使用临时文件避免内存占用
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            tmp_path = tmp.name
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zf:
                for student_dir in hw_dir.iterdir():
                    if student_dir.is_dir():
                        for file_path in student_dir.rglob("*"):
                            if file_path.is_file():
                                if flat:
                                    arcname = file_path.name
                                else:
                                    arcname = f"{student_dir.name}/{file_path.name}"
                                zf.write(file_path, arcname)
        # 分块读取临时文件并生成
        try:
            with open(tmp_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        finally:
            os.unlink(tmp_path)
