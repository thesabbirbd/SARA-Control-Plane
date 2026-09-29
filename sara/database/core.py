import aiosqlite
from typing import Optional, List
from sara.config.settings import settings
import logging

logger = logging.getLogger(__name__)

async def get_db():
    db = await aiosqlite.connect(settings.db_path)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    async with await get_db() as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                pid INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                exit_code INTEGER,
                error_message TEXT,
                log_path TEXT,
                parent_task_id INTEGER,
                depends_on INTEGER,
                batch_id TEXT,
                priority TEXT DEFAULT 'normal',
                retry_count INTEGER DEFAULT 0,
                next_attempt TIMESTAMP
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
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Initialize queue state
        await db.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('queue_paused', 'false')")
        
        await db.commit()

async def get_active_project(user_id: int) -> Optional[str]:
    async with await get_db() as db:
        async with db.execute("SELECT active_project FROM sessions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row['active_project'] if row else None

async def set_active_project(user_id: int, project: str):
    async with await get_db() as db:
        await db.execute(
            "INSERT INTO sessions (user_id, active_project) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET active_project = ?", 
            (user_id, project, project)
        )
        await db.commit()
