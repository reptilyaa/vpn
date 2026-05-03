import sqlite3
from datetime import datetime, timedelta

DB_NAME = "users.db"


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

    # CONFIGS (старая структура, чтобы не ломать существующую БД)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        public_key TEXT,
        config TEXT,
        created_at TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    # 🔥 АВТО-ОБНОВЛЕНИЕ СТРУКТУРЫ (если колонок нет — добавит)
    try:
        cur.execute("ALTER TABLE configs ADD COLUMN expires_at TEXT")
        print("✅ Добавлена колонка expires_at")
    except:
        pass

    try:
        cur.execute("ALTER TABLE configs ADD COLUMN plan TEXT")
        print("✅ Добавлена колонка plan")
    except:
        pass

    conn.commit()
    conn.close()


# ---------------- USERS ----------------
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


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()

    conn.close()
    return user


def get_active_configs():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT user_id, created_at
    FROM configs
    WHERE is_active = 1
    """)

    data = cur.fetchall()
    conn.close()
    return data


def is_active(user_id):
    user = get_user(user_id)
    if not user:
        return False

    trial_end = datetime.fromisoformat(user[1])
    return datetime.now() <= trial_end


# ---------------- CONFIGS ----------------
def save_config(user_id, public_key, config, days=7, plan="trial"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    expires_at = (datetime.now() + timedelta(days=days)).isoformat()

    cur.execute("""
    INSERT INTO configs (user_id, public_key, config, created_at, expires_at, plan)
    VALUES (?, ?, ?, datetime('now', '+3 hours'), ?, ?)
    """, (user_id, public_key, config, expires_at, plan))

    conn.commit()
    conn.close()


def get_user_configs(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT public_key FROM configs
    WHERE user_id=? AND is_active=1
    """)

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


# ---------------- EXPIRED ----------------
def get_expired_configs():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT public_key FROM configs
    WHERE is_active = 1 AND expires_at <= datetime('now')
    """)

    data = [row[0] for row in cur.fetchall()]

    cur.execute("""
    UPDATE configs
    SET is_active = 0
    WHERE is_active = 1 AND expires_at <= datetime('now')
    """)

    conn.commit()
    conn.close()

    return data