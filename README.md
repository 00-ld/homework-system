# 班级作业文件夹提交系统

一个功能完整的班级作业提交管理平台。支持 Web 端和微信小程序，管理员创建作业并生成专属链接，学生通过拖拽文件夹提交作业（最大 2GB），系统自动归档并支持导出。

🌐 **在线体验**: [web-production-de95b.up.railway.app](https://web-production-de95b.up.railway.app)

---

## 核心功能

### 👨‍🏫 管理员
- **多管理员注册** — 授权码 `work` 验证，支持多班级管理
- **作业管理** — 创建/查看/删除作业，设置截止日期，允许/禁止重交
- **提交详情** — 查看谁提交了、谁没提交，班级人员统计
- **系统管理** — 超管面板：系统统计、管理员管理、反馈查看
- **一键导出** — CSV 名单 + ZIP 打包下载（保留原始文件名）

### 👨‍🎓 学生
- **拖拽上传** — 直接拖拽文件夹到页面（支持 2GB 大文件）
- **提交状态** — 已提交/再次提交/截止禁用自动切换
- **记住账号** — localStorage 自动填充登录信息
- **反馈提交** — 意见与 Bug 一键反馈
- **手机适配** — 全页面响应式设计

### 📱 微信小程序
配套小程序项目位于 `miniprogram/`，通过 web-view 加载 Web 端。

---

## 快速开始

### 后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端（开发模式）
```bash
cd frontend
npm install
npm run dev
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python FastAPI + Uvicorn |
| 前端 | Vue 3 + Vite + Element Plus |
| 存储 | JSON 文件 / PostgreSQL |
| 部署 | Railway / Hugging Face Spaces |
| 小程序 | 微信小程序 web-view |

---

## 配置

编辑 `backend/config.py`:

```python
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB 上传上限
HOST = "0.0.0.0"
PORT = 8000
```
