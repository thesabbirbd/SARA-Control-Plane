import asyncio
import aiosqlite
import time

DB_PATH = "bench_queue.db"

async def setup_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                pid INTEGER,
                exit_code INTEGER,
                error_message TEXT,
                started_at TIMESTAMP,
                finished_at TIMESTAMP
            )
        ''')
        await db.execute("DELETE FROM tasks")

        # Insert 1000 tasks
        tasks = []
        for i in range(1000):
            tasks.append(("bench", "test", "RUNNING", 9999999 + i)) # Invalid PIDs
        await db.executemany(
            "INSERT INTO tasks (project_name, instruction, status, pid) VALUES (?, ?, ?, ?)",
            tasks
        )
        await db.commit()

async def transition_task(db, task_id: int, new_status: str, pid: int = None, exit_code: int = None, error_msg: str = None):
    # Dummy transition_task like the original
    async with db.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)) as c:
        row = await c.fetchone()
        if not row: raise ValueError(f"Task {task_id} not found")
        current_status = row[0]

    updates = ["status = ?"]
    params = [new_status]
    if new_status in ['SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED']:
        updates.append("finished_at = CURRENT_TIMESTAMP")

    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    params.append(task_id)
    await db.execute(query, params)

def is_process_alive(pid):
    return False

async def old_recovery():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status = 'RUNNING'") as cursor:
            tasks = await cursor.fetchall()
        for t in tasks:
            if not is_process_alive(t['pid']):
                await transition_task(db, t['id'], "INTERRUPTED")
        await db.commit()

async def new_recovery():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status = 'RUNNING'") as cursor:
            tasks = await cursor.fetchall()

        interrupted_ids = []
        for t in tasks:
            if not is_process_alive(t['pid']):
                interrupted_ids.append(t['id'])

        if interrupted_ids:
            # chunking or just an IN clause
            # for executemany
            params = [(id,) for id in interrupted_ids]
            await db.executemany("UPDATE tasks SET status = 'INTERRUPTED', finished_at = CURRENT_TIMESTAMP WHERE id = ?", params)

        await db.commit()

async def run_bench():
    await setup_db()
    start = time.time()
    await old_recovery()
    print(f"Old approach took: {time.time() - start:.4f} seconds")

    await setup_db()
    start = time.time()
    await new_recovery()
    print(f"New approach took: {time.time() - start:.4f} seconds")

asyncio.run(run_bench())
