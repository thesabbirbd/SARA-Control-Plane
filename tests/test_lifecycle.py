import sys
import os
import asyncio
import sqlite3
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import transition_task, init_db, DB_PATH
import aiosqlite

@pytest.mark.asyncio
async def test_lifecycle_transitions():
    # Setup
    test_db = DB_PATH + "_test"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    async with aiosqlite.connect(test_db) as db:
        await db.execute('''
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                pid INTEGER,
                exit_code INTEGER,
                error_message TEXT,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute("INSERT INTO tasks (project_name, instruction) VALUES ('test01', 'do something')")
        await db.commit()

        # Test valid transitions
        await transition_task(db, 1, 'STARTING')
        
        async with db.execute("SELECT status FROM tasks WHERE id = 1") as c:
            row = await c.fetchone()
            assert row[0] == 'STARTING'

        await transition_task(db, 1, 'RUNNING', pid=1234)
        
        async with db.execute("SELECT status, pid FROM tasks WHERE id = 1") as c:
            row = await c.fetchone()
            assert row[0] == 'RUNNING'
            assert row[1] == 1234

        await transition_task(db, 1, 'SUCCESS', exit_code=0)

        async with db.execute("SELECT status, exit_code FROM tasks WHERE id = 1") as c:
            row = await c.fetchone()
            assert row[0] == 'SUCCESS'
            assert row[1] == 0

        # Test illegal transition
        try:
            await transition_task(db, 1, 'STARTING')
            assert False, "Should have failed"
        except ValueError:
            pass # Expected
            
        # Retry hard override
        await transition_task(db, 1, 'PENDING')
        async with db.execute("SELECT status FROM tasks WHERE id = 1") as c:
            row = await c.fetchone()
            assert row[0] == 'PENDING'

    os.remove(test_db)
    print("Lifecycle tests passed!")

if __name__ == "__main__":
    asyncio.run(test_lifecycle_transitions())
