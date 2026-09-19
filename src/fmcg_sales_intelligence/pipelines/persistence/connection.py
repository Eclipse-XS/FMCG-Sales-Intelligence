from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import os
import psycopg

ROOT = PROJECT_ROOT
def load_env():
    path=ROOT/".env"
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line=raw.strip()
            if line and not line.startswith("#") and "=" in line:
                key,value=line.split("=",1);os.environ.setdefault(key,value)
def dsn():
    load_env()
    if os.getenv("DATABASE_URL"):return os.environ["DATABASE_URL"]
    values={"dbname":os.getenv("POSTGRES_DB","fmcg"),"user":os.getenv("POSTGRES_USER","fmcg"),"password":os.getenv("POSTGRES_PASSWORD","change_me"),"host":os.getenv("POSTGRES_HOST","localhost"),"port":os.getenv("POSTGRES_PORT","5432")}
    return " ".join(f"{key}={value}" for key,value in values.items())
def connect(*,autocommit=False):return psycopg.connect(dsn(),autocommit=autocommit)

