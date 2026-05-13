# 班级作业文件夹提交系统 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可直接安装使用的班级作业提交系统，管理员创建作业 + 生成提交链接，学生上传文件夹（≤500MB），自动按日期归档，支持导出 CSV。

**架构:** 前后端分离开发，PyInstaller 打包为单文件 exe。FastAPI 提供 RESTful API 并 serve 前端静态文件；Vue3 + Element Plus 提供管理后台和学生提交页面；JSON 文件系统存储，零数据库依赖。

**Tech Stack:** Python FastAPI, Vue3 + Vite + Element Plus, PyInstaller

---

### Task 0: 项目骨架 + 共享契约

**团队:** 架构工程师

**文件:**
- Create: `backend/config.py`
- Create: `backend/models/schemas.py`
- Create: `backend/storage/__init__.py`
- Create: `backend/api/__init__.py`
- Create: `backend/requirements.txt`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`

- [ ] **Step 1: 创建项目目录结构**

```bash
mkdir -p backend/api backend/models backend/storage
mkdir -p frontend/src/router frontend/src/api frontend/src/views frontend/src/components
mkdir -p scripts
```

- [ ] **Step 2: 写入后端配置文件 `backend/config.py`**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ADMIN_PASSWORD = "admin123"
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
HOST = "0.0.0.0"
PORT = 8000

# 确保数据目录存在
for d in [DATA_DIR, DATA_DIR / "uploads"]:
    os.makedirs(d, exist_ok=True)
```

- [ ] **Step 3: 写入 Pydantic 数据模型 `backend/models/schemas.py`**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SubmissionInfo(BaseModel):
    student_name: str
    student_id: str
    files: list[str] = []
    submitted_at: Optional[str] = None
    file_size: int = 0

class Homework(BaseModel):
    id: str
    title: str
    description: str
    due_date: str
    created_at: str
    link_id: str
    allow_resubmit: bool = False
    submissions: list[SubmissionInfo] = []

class LoginRequest(BaseModel):
    password: str

class CreateHomeworkRequest(BaseModel):
    title: str
    description: str
    due_date: str
    allow_resubmit: bool = False

class SubmitRequest(BaseModel):
    student_name: str
    student_id: str
```

- [ ] **Step 4: 写入 `backend/storage/__init__.py`**

```python
# JSON file storage engine
```

- [ ] **Step 5: 写入 `backend/api/__init__.py`**

```python
# API routes
```

- [ ] **Step 6: 写入 `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn==0.30.0
python-multipart==0.0.12
aiofiles==24.1.0
```

- [ ] **Step 7: 写入 `frontend/package.json`**

```json
{
  "name": "homework-submission-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "element-plus": "^2.8.0",
    "axios": "^1.7.0",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 8: 写入 `frontend/vite.config.js`**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
```

- [ ] **Step 9: 写入 `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>班级作业提交系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 10: 提交骨架**

```bash
git init
git add -A
git commit -m "chore: init project skeleton"
```

---

### Task 1: 后端存储引擎 + JSON 数据操作

**团队:** 架构/后端工程师

**文件:**
- Create: `backend/storage/json_store.py`
- Modify: `backend/storage/__init__.py`

- [ ] **Step 1: 写入 `backend/storage/json_store.py`**

```python
import json
import os
import shutil
import zipfile
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..config import DATA_DIR
from ..models.schemas import Homework, SubmissionInfo


class JsonStore:
    """JSON 文件存储引擎，负责作业元数据的 CRUD"""

    def __init__(self):
        self.homeworks_file = DATA_DIR / "homeworks.json"
        self.uploads_dir = DATA_DIR / "uploads"
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(self.uploads_dir, exist_ok=True)
        if not self.homeworks_file.exists():
            self._write_json([])

    def _read_json(self) -> list:
        try:
            with open(self.homeworks_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_json(self, data: list):
        with open(self.homeworks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _find_homework(self, homeworks: list, hw_id: str) -> Optional[dict]:
        for hw in homeworks:
            if hw["id"] == hw_id:
                return hw
        return None

    def create_homework(self, title: str, description: str, due_date: str, allow_resubmit: bool = False) -> dict:
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
        # 删除上传文件
        hw_dir = self.uploads_dir / f"{hw['due_date']}_{hw['title']}"
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
        # 检查是否已提交
        if not hw.get("allow_resubmit", False):
            for sub in hw.get("submissions", []):
                if sub["student_id"] == student_id:
                    return {"error": "duplicate", "message": "该学号已提交过作业"}
        sub = {
            "student_name": student_name,
            "student_id": student_id,
            "files": files,
            "submitted_at": datetime.now().isoformat(),
            "file_size": total_size
        }
        hw.setdefault("submissions", []).append(sub)
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

    def get_submission_dir(self, hw: dict, student_name: str, student_id: str) -> Path:
        dir_name = f"{hw['due_date']}_{hw['title']}"
        student_dir = self.uploads_dir / dir_name / f"{student_name}_{student_id}"
        os.makedirs(student_dir, exist_ok=True)
        return student_dir

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

    def create_submission_zip(self, hw_id: str) -> Optional[bytes]:
        hw = self.get_homework(hw_id)
        if not hw:
            return None
        dir_name = f"{hw['due_date']}_{hw['title']}"
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
                            arcname = f"{student_dir.name}/{file_path.relative_to(student_dir)}"
                            zf.write(file_path, arcname)
        buf.seek(0)
        return buf.getvalue()
```

- [ ] **Step 2: 更新 `backend/storage/__init__.py`**

```python
from .json_store import JsonStore

__all__ = ["JsonStore"]
```

---

### Task 2: 后端 API 路由

**团队:** 后端工程师

**文件:**
- Create: `backend/api/homework.py`
- Create: `backend/api/submission.py`
- Create: `backend/main.py`

- [ ] **Step 1: 写入 `backend/api/homework.py`**

```python
from fastapi import APIRouter, HTTPException, Header, Response
from ..models.schemas import LoginRequest, CreateHomeworkRequest
from ..storage import JsonStore
from ..config import ADMIN_PASSWORD

router = APIRouter(prefix="/api/admin", tags=["admin"])
store = JsonStore()


def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    if token != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="密码错误")


@router.post("/login")
def login(req: LoginRequest):
    if req.password == ADMIN_PASSWORD:
        return {"token": ADMIN_PASSWORD, "message": "登录成功"}
    raise HTTPException(status_code=401, detail="密码错误")


@router.post("/homeworks")
def create_homework(req: CreateHomeworkRequest, authorization: str = Header(None)):
    verify_token(authorization)
    hw = store.create_homework(
        title=req.title,
        description=req.description,
        due_date=req.due_date,
        allow_resubmit=req.allow_resubmit
    )
    return {"message": "创建成功", "homework": hw}


@router.get("/homeworks")
def list_homeworks(authorization: str = Header(None)):
    verify_token(authorization)
    return {"homeworks": store.list_homeworks()}


@router.get("/homeworks/{hw_id}")
def get_homework(hw_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    hw = store.get_homework(hw_id)
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")
    return {"homework": hw}


@router.delete("/homeworks/{hw_id}")
def delete_homework(hw_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    if store.delete_homework(hw_id):
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="作业不存在")


@router.get("/homeworks/{hw_id}/export-csv")
def export_csv(hw_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    csv_data = store.export_csv(hw_id)
    if csv_data is None:
        raise HTTPException(status_code=404, detail="作业不存在")
    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=submissions_{hw_id}.csv"}
    )


@router.get("/homeworks/{hw_id}/download-all")
def download_all(hw_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    zip_data = store.create_submission_zip(hw_id)
    if zip_data is None:
        raise HTTPException(status_code=404, detail="作业不存在或暂无提交")
    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=all_submissions_{hw_id}.zip"}
    )
```

- [ ] **Step 2: 写入 `backend/api/submission.py`**

```python
import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..models.schemas import SubmitRequest
from ..storage import JsonStore
from ..config import MAX_UPLOAD_SIZE

router = APIRouter(prefix="/api/submit", tags=["submit"])
store = JsonStore()


@router.get("/{link_id}")
def get_submit_page(link_id: str):
    hw = store.get_homework_by_link(link_id)
    if not hw:
        raise HTTPException(status_code=404, detail="链接无效或作业不存在")
    return {
        "homework": {
            "title": hw["title"],
            "description": hw["description"],
            "due_date": hw["due_date"],
            "link_id": hw["link_id"],
            "allow_resubmit": hw.get("allow_resubmit", False)
        }
    }


@router.post("/{link_id}")
async def submit_homework(
    link_id: str,
    student_name: str = Form(...),
    student_id: str = Form(...),
    files: list[UploadFile] = File(...)
):
    hw = store.get_homework_by_link(link_id)
    if not hw:
        raise HTTPException(status_code=404, detail="链接无效或作业不存在")

    # 检查是否已提交
    check = store.check_submission(link_id, student_name, student_id)
    if check and not hw.get("allow_resubmit", False):
        raise HTTPException(status_code=409, detail="该学号已提交过作业，不允许重复提交")
    if check and hw.get("allow_resubmit", False):
        # 允许重交时，删除旧文件
        old_dir = store.get_submission_dir(hw, student_name, student_id)
        if old_dir.exists():
            shutil.rmtree(old_dir)

    total_size = 0
    saved_files = []
    student_dir = store.get_submission_dir(hw, student_name, student_id)

    for file in files:
        content = await file.read()
        total_size += len(content)
        if total_size > MAX_UPLOAD_SIZE:
            # 清理已上传的文件
            shutil.rmtree(student_dir, ignore_errors=True)
            raise HTTPException(status_code=413, detail=f"文件总大小超过 {MAX_UPLOAD_SIZE // (1024*1024)}MB 限制")

        file_path = student_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        saved_files.append(file.filename)

    sub = store.save_submission(link_id, student_name, student_id, saved_files, total_size)
    if sub and "error" in sub:
        shutil.rmtree(student_dir, ignore_errors=True)
        raise HTTPException(status_code=409, detail=sub["message"])

    return {"message": "提交成功", "submission": sub}


@router.get("/{link_id}/check")
def check_submission(link_id: str, student_name: str, student_id: str):
    result = store.check_submission(link_id, student_name, student_id)
    return {"submitted": result is not None, "submission": result}
```

- [ ] **Step 3: 写入 `backend/main.py`**

```python
import webbrowser
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.homework import router as homework_router
from api.submission import router as submission_router
from config import HOST, PORT

app = FastAPI(title="班级作业提交系统")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(homework_router)
app.include_router(submission_router)

# 挂载前端静态文件（生产模式）
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 作业提交系统启动: http://localhost:{PORT}")
    print(f"📋 管理后台: http://localhost:{PORT}/#/admin/login")
    webbrowser.open(f"http://localhost:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
```

- [ ] **Step 4: 验证后端启动**

```bash
cd backend && pip install -r requirements.txt && python main.py
```

预期: 服务启动在 http://localhost:8000

---

### Task 3: 前端核心入口 + 路由 + API 封装

**团队:** 前端工程师

**文件:**
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 写入 `frontend/src/main.js`**

```javascript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.mount('#app')
```

- [ ] **Step 2: 写入 `frontend/src/App.vue`**

```vue
<template>
  <router-view />
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #f5f7fa;
}
</style>
```

- [ ] **Step 3: 写入 `frontend/src/router/index.js`**

```javascript
import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/admin/login' },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/AdminLogin.vue') },
  { path: '/admin/dashboard', name: 'AdminDashboard', component: () => import('@/views/AdminDashboard.vue') },
  { path: '/admin/homework/create', name: 'CreateHomework', component: () => import('@/views/CreateHomework.vue') },
  { path: '/admin/homework/:id', name: 'HomeworkDetail', component: () => import('@/views/HomeworkDetail.vue') },
  { path: '/submit/:linkId', name: 'StudentSubmit', component: () => import('@/views/StudentSubmit.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.path.startsWith('/admin') && to.path !== '/admin/login' && !token) {
    next('/admin/login')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 4: 写入 `frontend/src/api/index.js`**

```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 600000  // 10 min for large uploads
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.hash = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export function login(password) {
  return api.post('/admin/login', { password })
}

export function createHomework(data) {
  return api.post('/admin/homeworks', data)
}

export function listHomeworks() {
  return api.get('/admin/homeworks')
}

export function getHomework(id) {
  return api.get(`/admin/homeworks/${id}`)
}

export function deleteHomework(id) {
  return api.delete(`/admin/homeworks/${id}`)
}

export function exportCsv(id) {
  return api.get(`/admin/homeworks/${id}/export-csv`, { responseType: 'blob' })
}

export function downloadAll(id) {
  return api.get(`/admin/homeworks/${id}/download-all`, { responseType: 'blob' })
}

export function getSubmitPage(linkId) {
  return api.get(`/submit/${linkId}`)
}

export function submitHomework(linkId, formData, onProgress) {
  return api.post(`/submit/${linkId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  })
}

export function checkSubmission(linkId, name, studentId) {
  return api.get(`/submit/${linkId}/check`, { params: { student_name: name, student_id: studentId } })
}

export default api
```

---

### Task 4: 前端管理后台页面

**团队:** 前端工程师

**文件:**
- Create: `frontend/src/views/AdminLogin.vue`
- Create: `frontend/src/views/AdminDashboard.vue`
- Create: `frontend/src/views/CreateHomework.vue`
- Create: `frontend/src/views/HomeworkDetail.vue`

- [ ] **Step 1: 写入 `frontend/src/views/AdminLogin.vue`**

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">班级作业提交系统</h1>
      <p class="login-subtitle">管理员登录</p>
      <el-form @submit.prevent="handleLogin" label-width="0">
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="请输入管理员密码" show-password
            @keyup.enter="handleLogin" size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" size="large" style="width:100%">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!password.value) {
    ElMessage.warning('请输入密码')
    return
  }
  loading.value = true
  try {
    const res = await login(password.value)
    localStorage.setItem('admin_token', res.data.token)
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  width: 400px;
}
.login-title {
  text-align: center;
  font-size: 24px;
  color: #303133;
  margin: 0 0 8px;
}
.login-subtitle {
  text-align: center;
  color: #909399;
  margin: 0 0 32px;
  font-size: 14px;
}
</style>
```

- [ ] **Step 2: 写入 `frontend/src/views/AdminDashboard.vue`**

```vue
<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>作业管理</h1>
      <div>
        <el-button type="primary" @click="$router.push('/admin/homework/create')" size="large">
          <el-icon><Plus /></el-icon> 创建新作业
        </el-button>
        <el-button @click="logout" type="info" plain>退出登录</el-button>
      </div>
    </header>

    <el-table :data="homeworks" stripe style="width:100%" v-loading="loading" empty-text="暂无作业">
      <el-table-column prop="title" label="作业名称" min-width="180" />
      <el-table-column prop="due_date" label="截止日期" width="140" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="提交人数" width="100">
        <template #default="{ row }">
          <el-tag type="success">{{ row.submissions?.length || 0 }} 人</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="$router.push(`/admin/homework/${row.id}`)">
            查看
          </el-button>
          <el-button size="small" @click="copyLink(row)">
            <el-icon><Link /></el-icon> 复制链接
          </el-button>
          <el-popconfirm title="确定删除此作业？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listHomeworks, deleteHomework } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const homeworks = ref([])
const loading = ref(true)

async function fetchHomeworks() {
  loading.value = true
  try {
    const res = await listHomeworks()
    homeworks.value = res.data.homeworks
  } finally {
    loading.value = false
  }
}

function copyLink(row) {
  const link = `${window.location.origin}/#/submit/${row.link_id}`
  navigator.clipboard.writeText(link).then(() => {
    ElMessage.success('提交链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.info(`提交链接: ${link}`)
  })
}

async function handleDelete(id) {
  await deleteHomework(id)
  ElMessage.success('已删除')
  fetchHomeworks()
}

function logout() {
  localStorage.removeItem('admin_token')
  router.push('/admin/login')
}

onMounted(fetchHomeworks)
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.dashboard-header h1 { margin: 0; }
</style>
```

- [ ] **Step 3: 写入 `frontend/src/views/CreateHomework.vue`**

```vue
<template>
  <div class="create-page">
    <div class="create-card">
      <h1>创建新作业</h1>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" style="max-width:600px">
        <el-form-item label="作业名称" prop="title">
          <el-input v-model="form.title" placeholder="例：第三次作业" />
        </el-form-item>
        <el-form-item label="作业要求" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4"
            placeholder="描述作业内容、要求、注意事项等" />
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD"
            placeholder="选择截止日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="允许重交">
          <el-switch v-model="form.allow_resubmit" />
          <span style="margin-left:8px;color:#909399;font-size:13px">开启后学生可覆盖已提交的作业</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting" size="large">
            创建作业并生成链接
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>

      <el-alert v-if="created" type="success" :closable="false" style="margin-top:20px">
        <template #title>
          <p><strong>作业已创建！</strong></p>
          <p>提交链接：</p>
          <el-input :model-value="submitLink" readonly style="margin:8px 0">
            <template #append>
              <el-button @click="copyLink">复制链接</el-button>
            </template>
          </el-input>
          <p style="font-size:13px;color:#909399">将此链接发送给学生，他们打开后即可提交作业。</p>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createHomework } from '@/api'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const form = reactive({
  title: '',
  description: '',
  due_date: '',
  allow_resubmit: false
})
const rules = {
  title: [{ required: true, message: '请输入作业名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入作业要求', trigger: 'blur' }],
  due_date: [{ required: true, message: '请选择截止日期', trigger: 'change' }]
}
const submitting = ref(false)
const created = ref(false)
const submitLink = ref('')

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await createHomework(form)
    const linkId = res.data.homework.link_id
    submitLink.value = `${window.location.origin}/#/submit/${linkId}`
    created.value = true
    ElMessage.success('作业创建成功')
  } finally {
    submitting.value = false
  }
}

function copyLink() {
  navigator.clipboard.writeText(submitLink.value).then(() => {
    ElMessage.success('链接已复制')
  })
}
</script>

<style scoped>
.create-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}
.create-card {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.create-card h1 { margin: 0 0 24px; font-size: 22px; }
</style>
```

- [ ] **Step 4: 写入 `frontend/src/views/HomeworkDetail.vue`**

```vue
<template>
  <div class="detail-page" v-loading="loading">
    <el-button text @click="$router.push('/admin/dashboard')" style="margin-bottom:16px">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>

    <div v-if="hw" class="detail-card">
      <div class="hw-header">
        <div>
          <h1>{{ hw.title }}</h1>
          <p class="hw-desc">{{ hw.description }}</p>
          <p class="hw-meta">截止日期：{{ hw.due_date }} ｜ 已提交：{{ hw.submissions?.length || 0 }} 人</p>
        </div>
        <div class="hw-actions">
          <el-button type="success" @click="copyLink">
            <el-icon><Link /></el-icon> 复制提交链接
          </el-button>
          <el-button type="primary" @click="handleExport">
            <el-icon><Download /></el-icon> 导出 CSV
          </el-button>
          <el-button type="warning" @click="handleDownloadAll">
            <el-icon><FolderOpened /></el-icon> 下载全部文件
          </el-button>
        </div>
      </div>
      <el-tag :style="{marginBottom:'16px'}">
        提交链接：{{ fullLink }}
      </el-tag>

      <el-table :data="hw.submissions" stripe empty-text="暂无学生提交">
        <el-table-column prop="student_name" label="姓名" width="120" />
        <el-table-column prop="student_id" label="学号" width="140" />
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.submitted_at) }}
          </template>
        </el-table-column>
        <el-table-column label="文件" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="f in row.files" :key="f" style="margin:2px">{{ f }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="100">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getHomework, exportCsv, downloadAll } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const hw = ref(null)
const loading = ref(true)
const fullLink = computed(() => hw.value ? `${window.location.origin}/#/submit/${hw.value.link_id}` : '')

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}
function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
  return (bytes/(1024*1024)).toFixed(1) + ' MB'
}
function copyLink() {
  navigator.clipboard.writeText(fullLink.value)
  ElMessage.success('链接已复制')
}
async function handleExport() {
  const res = await exportCsv(route.params.id)
  const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv;charset=utf-8' }))
  const a = document.createElement('a')
  a.href = url; a.download = `submissions_${route.params.id}.csv`; a.click()
  URL.revokeObjectURL(url)
}
async function handleDownloadAll() {
  const res = await downloadAll(route.params.id)
  const url = URL.createObjectURL(new Blob([res.data], { type: 'application/zip' }))
  const a = document.createElement('a')
  a.href = url; a.download = `all_submissions_${route.params.id}.zip`; a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    const res = await getHomework(route.params.id)
    hw.value = res.data.homework
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.detail-card { background: white; padding: 32px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.hw-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.hw-header h1 { margin: 0 0 8px; font-size: 22px; }
.hw-desc { color: #606266; margin: 0 0 8px; white-space: pre-wrap; }
.hw-meta { color: #909399; font-size: 13px; margin: 0; }
.hw-actions { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
```

---

### Task 5: 前端学生提交页面 + 上传组件

**团队:** 前端工程师

**文件:**
- Create: `frontend/src/components/FolderUploader.vue`
- Create: `frontend/src/views/StudentSubmit.vue`

- [ ] **Step 1: 写入 `frontend/src/components/FolderUploader.vue`**

```vue
<template>
  <div class="uploader">
    <div class="drop-zone" @dragover.prevent @drop.prevent="handleDrop"
      :class="{ 'is-dragover': dragging }" @dragenter="dragging=true" @dragleave="dragging=false">
      <el-icon :size="48" color="#409eff"><FolderAdd /></el-icon>
      <p v-if="!files.length">拖拽文件夹到此处，或点击下方按钮选择</p>
      <p v-else class="file-count">已选择 {{ files.length }} 个文件</p>
    </div>

    <div style="margin-top:12px;text-align:center">
      <el-button type="primary" @click="selectFolder">
        <el-icon><FolderOpened /></el-icon> 选择文件夹
      </el-button>
      <input ref="fileInput" type="file" webkitdirectory multiple @change="handleFileSelect" hidden />
    </div>

    <div v-if="files.length" class="file-list">
      <div v-for="(f, i) in files" :key="i" class="file-item">
        <el-icon><Document /></el-icon>
        <span class="file-path">{{ f.relativePath || f.webkitRelativePath || f.name }}</span>
        <span class="file-size">{{ formatSize(f.size) }}</span>
      </div>
      <p class="file-total">
        共 {{ files.length }} 个文件，总计 {{ formatSize(totalSize) }}
        <span v-if="totalSize > maxSize" class="over-limit">
          （超过 {{ maxSize / (1024*1024) }}MB 限制！）
        </span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['files-change'])
const MAX_SIZE = 500 * 1024 * 1024
const maxSize = MAX_SIZE

const dragging = ref(false)
const files = ref([])
const fileInput = ref(null)

const totalSize = computed(() => files.value.reduce((s, f) => s + f.size, 0))

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
  return (bytes/(1024*1024)).toFixed(1) + ' MB'
}

function processFiles(fileList) {
  const arr = Array.from(fileList).map(f => {
    f.relativePath = f.webkitRelativePath || f.name
    return f
  })
  files.value = arr
  emit('files-change', arr, totalSize.value)
}

function selectFolder() {
  fileInput.value.value = ''
  fileInput.value.click()
}

function handleFileSelect(e) {
  if (e.target.files.length) processFiles(e.target.files)
}

function handleDrop(e) {
  dragging.value = false
  const items = e.dataTransfer.items
  if (items) {
    const promises = []
    for (const item of items) {
      if (item.webkitGetAsEntry) {
        promises.push(traverseEntry(item.webkitGetAsEntry()))
      }
    }
    Promise.all(promises).then(results => {
      const allFiles = results.flat()
      if (allFiles.length) processFiles(allFiles)
    })
  } else if (e.dataTransfer.files.length) {
    processFiles(e.dataTransfer.files)
  }
}

function traverseEntry(entry) {
  return new Promise(resolve => {
    if (entry.isFile) {
      entry.file(file => {
        file.relativePath = entry.fullPath.replace(/^\//, '')
        resolve([file])
      })
    } else if (entry.isDirectory) {
      const reader = entry.createReader()
      const allEntries = []
      function readEntries() {
        reader.readEntries(entries => {
          if (entries.length) {
            allEntries.push(...entries)
            readEntries()
          } else {
            resolve(Promise.all(allEntries.map(e => traverseEntry(e))).then(r => r.flat()))
          }
        })
      }
      readEntries()
    } else {
      resolve([])
    }
  })
}

defineExpose({ files, totalSize, getFiles: () => files.value })
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}
.drop-zone:hover, .drop-zone.is-dragover {
  border-color: #409eff;
  background: #ecf5ff;
}
.drop-zone p { color: #909399; margin: 8px 0 0; }
.file-count { font-size: 16px; color: #409eff !important; }
.file-list { margin-top: 16px; max-height: 300px; overflow-y: auto; }
.file-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; font-size: 13px; color: #606266;
}
.file-item:nth-child(odd) { background: #fafafa; }
.file-path { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { color: #909399; white-space: nowrap; }
.file-total { font-size: 14px; font-weight: bold; margin: 8px 0 0; text-align: right; }
.over-limit { color: #f56c6c; }
</style>
```

- [ ] **Step 2: 写入 `frontend/src/views/StudentSubmit.vue`**

```vue
<template>
  <div class="submit-page" v-loading="loading">
    <div class="submit-card" v-if="hw">
      <el-alert v-if="submitted" type="success" :closable="false" style="margin-bottom:20px">
        <template #title>提交成功！作业已提交完毕。</template>
      </el-alert>

      <h1>{{ hw.title }}</h1>
      <div class="hw-info">
        <p>{{ hw.description }}</p>
        <el-tag>截止日期：{{ hw.due_date }}</el-tag>
        <el-tag v-if="hw.allow_resubmit" type="warning">允许重复提交</el-tag>
      </div>

      <el-divider />

      <h2>提交作业</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入您的姓名" />
        </el-form-item>
        <el-form-item label="学号" prop="studentId">
          <el-input v-model="form.studentId" placeholder="请输入您的学号" />
        </el-form-item>
      </el-form>

      <FolderUploader ref="uploaderRef" @files-change="onFilesChange" />

      <div style="margin-top:20px">
        <el-button type="primary" @click="handleSubmit" :loading="uploading" size="large"
          :disabled="!canSubmit" style="width:100%">
          {{ uploading ? '上传中...' : '提交作业' }}
        </el-button>
      </div>

      <el-progress v-if="uploading" :percentage="progress" style="margin-top:16px" :stroke-width="16" />

      <div v-if="errorMsg" style="margin-top:12px">
        <el-alert :title="errorMsg" type="error" :closable="false" />
      </div>
    </div>

    <div v-else-if="!loading" class="submit-card" style="text-align:center;padding:60px">
      <el-icon :size="64" color="#f56c6c"><WarningFilled /></el-icon>
      <h2>链接无效</h2>
      <p>该提交链接不存在或已过期，请联系老师获取新链接。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSubmitPage, submitHomework, checkSubmission } from '@/api'
import { ElMessage } from 'element-plus'
import FolderUploader from '@/components/FolderUploader.vue'

const route = useRoute()
const hw = ref(null)
const loading = ref(true)
const submitting = ref(false)
const uploaded = ref(false)
const errorMsg = ref('')
const progress = ref(0)
const formRef = ref(null)
const uploaderRef = ref(null)
const MAX_SIZE = 500 * 1024 * 1024

const form = reactive({ name: '', studentId: '' })
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  studentId: [{ required: true, message: '请输入学号', trigger: 'blur' }]
}

const currentFiles = ref([])
const currentTotalSize = ref(0)
const canSubmit = computed(() => currentFiles.value.length > 0 && currentTotalSize.value <= MAX_SIZE)

function onFilesChange(files, totalSize) {
  currentFiles.value = files
  currentTotalSize.value = totalSize
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!currentFiles.value.length) {
    errorMsg.value = '请先选择要上传的文件夹'
    return
  }
  if (currentTotalSize.value > MAX_SIZE) {
    errorMsg.value = '文件总大小超过 500MB 限制，请减少文件后重试'
    return
  }

  const formData = new FormData()
  formData.append('student_name', form.name)
  formData.append('student_id', form.studentId)
  for (const file of currentFiles.value) {
    formData.append('files', file, file.relativePath || file.name)
  }

  errorMsg.value = ''
  try {
    await submitHomework(route.params.linkId, formData, (e) => {
      progress.value = Math.round((e.loaded / e.total) * 100)
    })
    ElMessage.success('提交成功！')
    submitted.value = true
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '提交失败，请重试'
  }
}

onMounted(async () => {
  try {
    const res = await getSubmitPage(route.params.linkId)
    hw.value = res.data.homework
  } catch {
    hw.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.submit-page {
  display: flex; justify-content: center;
  min-height: 100vh; background: #f5f7fa; padding: 40px 16px;
}
.submit-card {
  background: white; padding: 40px; border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); width: 100%; max-width: 700px;
}
.submit-card h1 { margin: 0 0 12px; font-size: 22px; }
.submit-card h2 { font-size: 18px; margin: 0 0 16px; }
.hw-info p { color: #606266; margin: 0 0 12px; white-space: pre-wrap; }
.hw-info .el-tag { margin-right: 8px; }
</style>
```

---

### Task 6: 打包 + 构建脚本 + README

**团队:** 运维打包工程师

**文件:**
- Create: `scripts/build.bat`
- Create: `scripts/build.sh`
- Create: `start.bat`
- Create: `start.sh`
- Create: `homework_submission_system.spec`
- Create: `README.md`

- [ ] **Step 1: 写入 `scripts/build.bat`**

```bat
@echo off
chcp 65001 >nul
echo ========================================
echo  班级作业提交系统 - 构建打包脚本
echo ========================================

echo.
echo [1/3] 安装后端依赖...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 ( echo 安装失败! & pause & exit /b 1 )
cd ..

echo.
echo [2/3] 构建前端...
cd frontend
call npm install
if %errorlevel% neq 0 ( echo npm install 失败! & pause & exit /b 1 )
call npm run build
if %errorlevel% neq 0 ( echo 前端构建失败! & pause & exit /b 1 )
cd ..

echo.
echo [3/3] 打包为可执行文件...
pip install pyinstaller
if exist "dist\homework_submission_system" rmdir /s /q "dist\homework_submission_system"
pyinstaller homework_submission_system.spec
if %errorlevel% neq 0 ( echo 打包失败! & pause & exit /b 1 )

echo.
echo ========================================
echo  打包完成！
echo  可执行文件: dist\homework_submission_system\homework_submission_system.exe
echo ========================================
pause
```

- [ ] **Step 2: 写入 `scripts/build.sh`**

```bash
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
```

- [ ] **Step 3: 写入 `start.bat`**

```bat
@echo off
chcp 65001 >nul
title 班级作业提交系统
echo ========================================
echo  班级作业提交系统 正在启动...
echo ========================================

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
```

- [ ] **Step 4: 写入 `start.sh`**

```bash
#!/bin/bash
echo "===== 班级作业提交系统 ====="
cd backend
pip install -r requirements.txt -q
echo "启动服务: http://localhost:8000"
python main.py
```

- [ ] **Step 5: 写入 `homework_submission_system.spec`**

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

frontend_dist = Path(__file__).parent / "frontend" / "dist"

a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (str(frontend_dist / "*"), "frontend/dist"),
    ],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops.auto', 'uvicorn.protocols.http.auto'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='homework_submission_system',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
```

- [ ] **Step 6: 写入 `README.md`**

```markdown
# 班级作业文件夹提交系统

一个基于 Web 的班级作业提交工具。管理员创建作业并生成专属链接，学生通过链接提交文件夹（≤500MB），系统自动按日期归档。

## 快速开始

### 方式一：直接运行（开发模式）

```bash
# Windows
start.bat

# Mac / Linux
bash start.sh
```

浏览器自动打开 → 访问 `http://localhost:8000`

### 方式二：打包为可执行文件

```bash
# Windows
scripts\build.bat

# Mac / Linux
bash scripts/build.sh
```

打包后在 `dist/` 目录下生成可执行文件。

## 使用指南

### 管理员
1. 打开系统，进入管理后台
2. 默认密码：`admin123`（可在 `backend/config.py` 修改）
3. 创建作业 → 填写名称、要求、截止日期
4. 复制系统生成的提交链接，发送给学生

### 学生
1. 打开老师发的链接
2. 填写姓名和学号
3. 选择或拖拽文件夹上传（≤500MB）
4. 等待上传完成，看到"提交成功"提示

### 教师管理
- 在作业详情页查看提交名单
- 导出提交记录 CSV
- 一键下载所有提交文件

## 配置说明

编辑 `backend/config.py`：

```python
ADMIN_PASSWORD = "admin123"           # 管理员密码
MAX_UPLOAD_SIZE = 500 * 1024 * 1024   # 最大上传大小（500MB）
HOST = "0.0.0.0"                      # 监听地址
PORT = 8000                           # 监听端口
```

## 技术栈

- 后端：Python FastAPI
- 前端：Vue 3 + Element Plus
- 存储：JSON 文件系统（无需数据库）
- 打包：PyInstaller
```

---

### Task 7: 验证 + 联调

**团队:** 所有

- [ ] **Step 1: 验证后端启动**

```bash
cd backend && pip install -r requirements.txt && python main.py
```

预期: 服务启动在 http://localhost:8000

- [ ] **Step 2: 验证前端启动（开发模式）**

```bash
cd frontend && npm install && npm run dev
```

预期: Vite 启动在 http://localhost:5173，API 代理到 8000

- [ ] **Step 3: 验证端到端流程**

```bash
# 1. 管理员登录
curl -X POST http://localhost:8000/api/admin/login -H "Content-Type: application/json" -d '{"password":"admin123"}'
# 预期: {"token":"admin123","message":"登录成功"}

# 2. 创建作业
curl -X POST http://localhost:8000/api/admin/homeworks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin123" \
  -d '{"title":"测试作业","description":"请提交实验报告","due_date":"2026-05-20"}'
# 预期: 返回 homework 对象包含 link_id

# 3. 获取提交页面（用上一步的 link_id）
curl http://localhost:8000/api/submit/{link_id}
# 预期: 返回作业信息

# 4. 提交作业
curl -X POST http://localhost:8000/api/submit/{link_id} \
  -F "student_name=张三" \
  -F "student_id=2024001" \
  -F "files=@test.txt"
# 预期: {"message":"提交成功"}

# 5. 导出 CSV
curl -H "Authorization: Bearer admin123" http://localhost:8000/api/admin/homeworks/{id}/export-csv
# 预期: 返回 CSV 文件内容
```

- [ ] **Step 4: 验证 500MB 限制**

```bash
# 创建一个测试大文件（谨慎，仅测试）
dd if=/dev/zero of=large_test.bin bs=1M count=501 2>/dev/null
curl -X POST http://localhost:8000/api/submit/{link_id} \
  -F "student_name=测试" -F "student_id=9999" \
  -F "files=@large_test.bin"
# 预期: 413 文件过大
rm large_test.bin
```
