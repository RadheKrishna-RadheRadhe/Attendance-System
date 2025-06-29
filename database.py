import sqlite3
from datetime import datetime

DB_FILE = "attendance.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                reg_number TEXT UNIQUE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TEXT
            )
        """)
        conn.commit()

def add_user(name, reg_number):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (name, reg_number) VALUES (?, ?)", (name, reg_number))
        conn.commit()
        return c.lastrowid

def get_user_id_by_reg_number(reg_number):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE reg_number = ?", (reg_number,))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            raise ValueError(f"Reg number '{reg_number}' not found in database.")

def get_user_name(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else None

def get_user_reg_number(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT reg_number FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else None

def log_attendance(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO attendance (user_id, timestamp) VALUES (?, ?)",
            (user_id, datetime.now().isoformat())
        )
        conn.commit()
