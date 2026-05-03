import sqlite3
from datetime import datetime, timedelta

DB_NAME = "users.db"


# ---------------- TIME (МСК) ----------------
def now_msk():
    return datetime.utcnow() + timedelta(hours=3)


# ---------------- INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        trial_end TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    # CONFIGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        public_key TEXT,
        config TEXT,
        created_at TEXT,
        expires_at TEXT,
        plan TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# ---------------- USERS ----------------
def create_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    trial_end = (now_msk() + timedelta(days=7)).isoformat()

    cur.execute("""
    INSERT OR IGNORE INTO users (user_id, trial_end, active)
    VALUES (?, ?, 1)
    """, (user_id, trial_end))

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    conn.close()
    return user


def is_active(user_id):
    user = get_user(user_id)
    if not user:
        return False

    trial_end = datetime.fromisoformat(user[1])
    return now_msk() <= trial_end


# ---------------- CONFIGS ----------------
def save_config(user_id, public_key, config, days=7, plan="trial"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    expires_at = (now_msk() + timedelta(days=days)).isoformat()
    created_at = now_msk().isoformat()

    cur.execute("""
    INSERT INTO configs (user_id, public_key, config, created_at, expires_at, plan)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, public_key, config, created_at, expires_at, plan))

    conn.commit()
    conn.close()


def get_user_configs(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT public_key FROM configs
    WHERE user_id=? AND is_active=1
    """, (user_id,))   # ✅ FIX

    data = cur.fetchall()
    conn.close()
    return data


def deactivate_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    UPDATE configs
    SET is_active = 0
    WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def delete_user_configs(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM configs
    WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


# ---------------- EXPIRED ----------------
def get_expired_configs():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT public_key FROM configs
    WHERE is_active = 1 AND expires_at <= ?
    """, (now_msk().isoformat(),))

    data = [row[0] for row in cur.fetchall()]

    cur.execute("""
    UPDATE configs
    SET is_active = 0
    WHERE is_active = 1 AND expires_at <= ?
    """, (now_msk().isoformat(),))

    conn.commit()
    conn.close()

    return data