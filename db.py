import sqlite3
from contextlib import closing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "opinion_ai.db"


def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def query_one(sql, params=()):
    with closing(get_db()) as conn:
        return conn.execute(sql, params).fetchone()


def query_all(sql, params=()):
    with closing(get_db()) as conn:
        return conn.execute(sql, params).fetchall()


def execute(sql, params=()):
    with closing(get_db()) as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid


def execute_many(sql, params_list):
    with closing(get_db()) as conn:
        conn.executemany(sql, params_list)
        conn.commit()
