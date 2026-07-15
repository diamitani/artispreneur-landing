"""Database helpers."""
import psycopg2
import psycopg2.extras
from typing import Any, Sequence
from app.config import config


def connect():
    return psycopg2.connect(
        host=config.db_host, dbname=config.db_name,
        user=config.db_user, password=config.db_pass,
    )


def fetch_one(query: str, params: Sequence[Any] = ()):
    db = connect()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close(); db.close()
    return dict(row) if row else None


def fetch_all(query: str, params: Sequence[Any] = ()):
    db = connect()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); db.close()
    return rows


def execute(query: str, params: Sequence[Any] = ()):
    db = connect()
    cur = db.cursor()
    cur.execute(query, params)
    db.commit()
    cur.close(); db.close()
