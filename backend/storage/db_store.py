"""
PostgreSQL 存储后端 - 用于云部署（Zeabur + Supabase）
提供与 JSON 文件完全相同的数据存取接口，
底层用 PostgreSQL 的 JSONB 字段存储，数据持久化不丢失。
"""
import json
import os
from typing import Optional
from datetime import datetime


def _get_conn():
    import psycopg2
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    """创建数据表（幂等）"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_store (
            key TEXT PRIMARY KEY,
            value JSONB NOT NULL DEFAULT '{}'::jsonb,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def _load(key: str, default=None):
    """从 PostgreSQL 读取 JSON 数据"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM app_store WHERE key = %s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0]
    return default if default is not None else ([] if key.endswith("s") else {})


def _save(key: str, data):
    """写入 JSON 数据到 PostgreSQL"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO app_store (key, value, updated_at)
        VALUES (%s, %s::jsonb, NOW())
        ON CONFLICT (key) DO UPDATE SET value = %s::jsonb, updated_at = NOW()
    """, (key, json.dumps(data, ensure_ascii=False), json.dumps(data, ensure_ascii=False)))
    conn.commit()
    cur.close()
    conn.close()


# ─── 以下方法完全模仿 JsonStore 的读写模式 ───

def read_admins() -> list:
    return _load("admins", [])

def write_admins(data: list):
    _save("admins", data)

def read_students() -> list:
    return _load("students", [])

def write_students(data: list):
    _save("students", data)

def read_homeworks() -> list:
    return _load("homeworks", [])

def write_homeworks(data: list):
    _save("homeworks", data)

def read_classes() -> list:
    return _load("classes", [])

def write_classes(data: list):
    _save("classes", data)

def read_email_config() -> dict:
    return _load("email_config", {})

def write_email_config(data: dict):
    _save("email_config", data)

# 改进11: 反馈存储
def read_feedbacks() -> list:
    return _load("feedbacks", [])

def write_feedbacks(data: list):
    _save("feedbacks", data)
