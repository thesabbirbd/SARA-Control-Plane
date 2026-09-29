import aiosqlite
from app.core.config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                pid INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                active_project TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notify_enabled INTEGER DEFAULT 1
            )
        ''')
        try:
            await db.execute("ALTER TABLE sessions ADD COLUMN notify_enabled INTEGER DEFAULT 1")
        except Exception:
            pass
        await db.commit()

async def get_active_project(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT active_project FROM sessions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_active_project(user_id: int, project: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO sessions (user_id, active_project) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET active_project = excluded.active_project, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, project))
        await db.commit()

async def get_notify_preference(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT notify_enabled FROM sessions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row[0]) if row else True

async def toggle_notify_preference(user_id: int) -> bool:
    current = await get_notify_preference(user_id)
    new_val = 0 if current else 1
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO sessions (user_id, notify_enabled) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET notify_enabled = excluded.notify_enabled
        ''', (user_id, new_val))
        await db.commit()
    return bool(new_val)

