import aiosqlite
from app.core.config import DB_PATH

async def queue_task(project: str, instruction: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO tasks (project_name, instruction, status)
            VALUES (?, ?, 'PENDING')
        ''', (project, instruction))
        await db.commit()
        return cursor.lastrowid

async def get_tasks(limit=5):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            return await cursor.fetchall()

async def get_task(task_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            return await cursor.fetchone()

async def update_task_status(task_id: int, status: str, pid: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if pid is not None:
            await db.execute("UPDATE tasks SET status = ?, pid = ? WHERE id = ?", (status, pid, task_id))
        else:
            await db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        await db.commit()

async def get_pending_task():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY id ASC LIMIT 1") as cursor:
            return await cursor.fetchone()

async def scheduled_db_insert(project, instruction):
    await queue_task(project, instruction)
