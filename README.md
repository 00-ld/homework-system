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
