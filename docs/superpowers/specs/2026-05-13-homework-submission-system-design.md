# 班级作业文件夹提交系统 - 设计文档

## 概述

一个基于 Web 的班级作业提交系统，管理员创建作业并生成专属提交链接，学生通过链接提交文件夹（≤500MB），系统自动按日期归档。打包为独立可执行文件，双击即用。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python FastAPI | RESTful API + 静态文件服务 |
| 前端 | Vue 3 + Vite + Element Plus | 管理后台 + 学生提交页 |
| 存储 | JSON 文件 | 本地文件系统，无数据库依赖 |
| 打包 | PyInstaller | 打包为单文件 .exe |

## 目录结构

```
homework-submission-system/
├── backend/
│   ├── main.py                 # FastAPI 应用入口 + 静态文件挂载
│   ├── api/
│   │   ├── __init__.py
│   │   ├── homework.py         # 作业管理路由
│   │   └── submission.py       # 学生提交路由（公开）
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic 数据模型
│   ├── storage/
│   │   ├── __init__.py
│   │   └── json_store.py       # JSON 文件读写引擎
│   ├── config.py               # 全局配置（密码、路径、大小限制）
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js        # Vue Router 路由配置
│   │   ├── api/
│   │   │   └── index.js        # Axios API 封装
│   │   ├── views/
│   │   │   ├── AdminLogin.vue       # 管理员登录
│   │   │   ├── AdminDashboard.vue   # 作业列表 + 管理
│   │   │   ├── CreateHomework.vue   # 创建/编辑作业
│   │   │   ├── HomeworkDetail.vue   # 作业详情 + 提交名单
│   │   │   └── StudentSubmit.vue    # 学生提交页面
│   │   └── components/
│   │       └── FolderUploader.vue   # 文件夹上传组件（拖拽+选择）
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/                       # 运行时自动生成
│   ├── homeworks.json          # 作业元数据
│   └── uploads/                # 提交文件存储
│       └── {作业日期}/
│           └── {学生姓名_学号}/
│               └── (上传的文件)
├── scripts/
│   ├── build.bat               # 构建 & 打包脚本
│   └── build.sh
├── start.bat                   # 开发/运行启动脚本
├── start.sh
└── README.md                   # 使用说明
```

## API 接口

### 管理端（需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login` | 登录，返回 token |
| POST | `/api/admin/homeworks` | 创建作业 |
| GET | `/api/admin/homeworks` | 获取作业列表 |
| GET | `/api/admin/homeworks/{id}` | 获取作业详情 |
| DELETE | `/api/admin/homeworks/{id}` | 删除作业 |
| GET | `/api/admin/homeworks/{id}/export-csv` | 导出提交名单 CSV |
| GET | `/api/admin/homeworks/{id}/download-all` | 下载所有提交文件 (zip) |

### 学生端（公开，通过 link_id 访问）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/submit/{link_id}` | 获取作业信息 |
| POST | `/api/submit/{link_id}` | 提交作业（含文件上传） |
| GET | `/api/submit/{link_id}/check` | 查询某学生的提交状态 |

## 数据模型

### Homework（作业）

```json
{
  "id": "uuid",
  "title": "第三次作业",
  "description": "完成课后习题1-5",
  "due_date": "2026-05-20",
  "created_at": "2026-05-13T10:00:00",
  "link_id": "abc123-def456",
  "submissions": [
    {
      "student_name": "张三",
      "student_id": "2024001",
      "files": ["file1.pdf", "file2.py"],
      "submitted_at": "2026-05-14T15:30:00",
      "file_size": 1048576
    }
  ]
}
```

## 核心数据流

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│ 管理员登录    │────>│ 创建作业        │────>│ 生成提交链接    │
│ (密码认证)    │     │ (日期/要求)     │     │ (UUID)        │
└─────────────┘     └───────────────┘     └──────┬───────┘
                                                 │ 分享链接
                                                 ▼
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│ 学生打开链接   │────>│ 填写信息 +      │────>│ 后端校验 +     │
│ (无需登录)    │     │ 上传文件夹      │     │ 存储归档       │
└─────────────┘     └───────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│ 管理员查看名单 │<────│ 导出 CSV       │<────│ data/uploads/ │
│ + 下载文件    │     │ + 下载压缩包    │     │ 按日期归档     │
└─────────────┘     └───────────────┘     └──────────────┘
```

## 关键设计决策

1. **零数据库**：全部 JSON + 文件系统存储，开箱即用无需配置
2. **认证简洁**：固定管理员密码（配置在 config.py，可修改）
3. **文件夹上传**：前端使用 `<input webkitdirectory>` 选择文件夹，也支持拖拽
4. **双重校验**：前端上传前检查文件大小，后端接收时再次校验，超 500MB 拒绝
5. **Link 鉴权**：每个作业生成唯一 UUID link_id，学生凭链接访问，无需注册
6. **按日期归档**：`data/uploads/{作业日期}/{学生姓名_学号}/` 结构
7. **CSV 导出**：包含姓名、学号、提交时间、文件列表、文件大小
8. **跨域**：开发模式后端 `/api/*` 加 CORS 头；生产模式由 FastAPI 直接 serve 前端

## 错误处理

- 文件超限 → 413 Payload Too Large
- link_id 无效 → 404 Not Found
- 重复提交 → 409 Conflict（同一学生可覆盖或拒绝）
- 目录不存在 → 自动创建
- JSON 文件损坏 → 备份 + 重建

## 打包部署

### 开发模式
```bash
# 终端1：后端
cd backend && pip install -r requirements.txt && python main.py

# 终端2：前端
cd frontend && npm install && npm run dev
```

### 生产打包（给同学用）
```bash
cd frontend && npm run build          # 前端构建到 dist/
cd .. && pyinstaller -F backend/main.py --add-data "frontend/dist;frontend/dist"
# 生成 dist/作业提交系统.exe
```

### 使用方式
1. 双击 `作业提交系统.exe`
2. 自动打开浏览器进入 `http://localhost:8000`
3. 管理员登录 → 创建作业 → 分享链接给同学
4. 同学打开链接 → 提交作业

## 实现计划

项目拆分为 4 个独立工作包，可并行开发：

| 团队 | 职责 | 文件 |
|------|------|------|
| 架构 | 项目骨架、API 定义、数据模型 | backend/config.py, models/*, schemas.py |
| 后端 | API 路由、存储引擎、文件处理 | backend/api/*, storage/*, main.py |
| 前端 | Vue3 页面、上传组件、API 对接 | frontend/src/* |
| 打包 | 构建脚本、启动脚本、README | scripts/*, start.*, README.md |

### 依赖关系

```
架构 ──→ 后端 ──→ 前端 ──→ 打包
       ↘-------↗
```

架构和后端可先启动，前端需要 API 定型后对接，打包需要前后端都完成。
