FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制后端和前端
COPY backend/ backend/
COPY --from=frontend /frontend/dist frontend/dist/

# Zeabur 会设置 PORT 环境变量
# Supabase 数据库连接串通过 Zeabur 环境变量 DATABASE_URL 注入
EXPOSE 8000

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
