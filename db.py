import sqlite3
import json
import os
import re
from kivy.app import App

TYPE_MAP = {
    "Текст": "TEXT",
    "Число": "NUMERIC",
    "Дата": "TEXT",
    "Время": "TEXT",
    "Да/Нет": "INTEGER",
}

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    ' ': '_', '-': '_',
}

def get_db_path():
    return os.path.join(App.get_running_app().user_data_dir, "anytable.db")

def get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def slugify(name):
    result = [ _TRANSLIT.get(ch, ch) if ch in _TRANSLIT or (ch.isalnum() and ord(ch) < 128) else "" for ch in name.lower() ]
    s = "".join(result).strip("_")
    return ("t_" + s) if (not s or s[0].isdigit()) else (s or "table")

def safe_name(name):
    if re.search(r'["\';]', name):
        raise ValueError(f"Недопустимое имя: {name}")
    return name

def q(name):
    return '"' + safe_name(name).replace('"', '""') + '"'

def format_value(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v) if v is not None else ""

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tables_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            display_name TEXT,
            columns TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_table(display_name, columns):
    name = slugify(display_name)
    safe_name(name)
    conn = get_conn()
    try:
        existing = conn.execute("SELECT 1 FROM tables_registry WHERE name = ?", (name,)).fetchone()
        if existing:
            i = 2
            while True:
                candidate = f"{name}_{i}"
                if not conn.execute("SELECT 1 FROM tables_registry WHERE name = ?", (candidate,)).fetchone():
                    name = candidate
                    break
                i += 1

        conn.execute(
            "INSERT INTO tables_registry (name, display_name, columns) VALUES (?, ?, ?)",
            (name, display_name, json.dumps(columns, ensure_ascii=False))
        )
        fields = ", ".join(f"{q(c['name'])} {TYPE_MAP.get(c['type'], 'TEXT')}" for c in columns)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {q(name)} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {fields},
                created_at INTEGER
            )
        """)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_tables():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tables_registry").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_table(name):
    conn = get_conn()
    row = conn.execute("SELECT * FROM tables_registry WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_row(table_name, data):
    safe_name(table_name)
    conn = get_conn()
    cols = ", ".join([q(k) for k in data.keys()])
    placeholders = ", ".join(["?"] * len(data))
    conn.execute(
        f"INSERT INTO {q(table_name)} ({cols}, created_at) VALUES ({placeholders}, strftime('%s','now'))",
        list(data.values())
    )
    conn.commit()
    conn.close()

def update_row(table_name, row_id, data):
    safe_name(table_name)
    conn = get_conn()
    sets = ", ".join([f"{q(k)} = ?" for k in data.keys()])
    params = list(data.values()) + [row_id]
    conn.execute(f"UPDATE {q(table_name)} SET {sets} WHERE id = ?", params)
    conn.commit()
    conn.close()

def get_rows(table_name, filters=None, order_by=None, desc=True):
    safe_name(table_name)
    conn = get_conn()
    sql = f"SELECT * FROM {q(table_name)}"
    params = []
    conditions = []

    if filters:
        for k, op, v in filters:
            safe_name(k)
            if op == "LIKE":
                conditions.append(f"({q(k)} IS NOT NULL AND {q(k)} != '' AND {q(k)} LIKE ?)")
                params.append(f"%{v}%")
            else:
                conditions.append(f"({q(k)} IS NOT NULL AND {q(k)} != '' AND {q(k)} {op} ?)")
                params.append(v)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    if order_by:
        safe_name(order_by)
        sql += f" ORDER BY {q(order_by)} {'DESC' if desc else 'ASC'}"

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_row(table_name, row_id):
    safe_name(table_name)
    conn = get_conn()
    conn.execute(f"DELETE FROM {q(table_name)} WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()

def delete_table(name):
    safe_name(name)
    conn = get_conn()
    conn.execute(f"DROP TABLE IF EXISTS {q(name)}")
    conn.execute("DELETE FROM tables_registry WHERE name = ?", (name,))
    conn.commit()
    conn.close()