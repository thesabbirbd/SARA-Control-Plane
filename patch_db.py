import asyncio
import aiosqlite
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("SARA_DB_PATH", os.path.join(PROJECT_ROOT, "queue.db"))

async def migrate():
    async with aiosqlite.connect(DB_PATH) as db:
        columns_to_add = [
            ("started_at", "TIMESTAMP"),
            ("finished_at", "TIMESTAMP"),
            ("exit_code", "INTEGER"),
            ("retry_count", "INTEGER DEFAULT 0"),
            ("error_message", "TEXT"),
            ("log_path", "TEXT"),
            ("parent_task_id", "INTEGER")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                await db.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                pass
                
        await db.commit()

asyncio.run(migrate())
