import sqlite3
from datetime import datetime, timedelta

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        trial_end TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    conn.close()
    return user


def create_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    trial_end = (datetime.now() + timedelta(days=7)).isoformat()

    cur.execute("""
    INSERT OR IGNORE INTO users (user_id, trial_end, active)
    VALUES (?, ?, 1)
    """, (user_id, trial_end))

    conn.commit()
    conn.close()


def is_active(user_id):
    user = get_user(user_id)
    if not user:
        return False

    trial_end = datetime.fromisoformat(user[1])

    if datetime.now() > trial_end:
        return False

    return True