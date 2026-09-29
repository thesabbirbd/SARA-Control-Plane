import asyncio
from sara.database.core import get_db

async def run_v1_3_100_migrations():
    async with get_db() as db:
        # Operational Memory
        await db.execute('''
        CREATE TABLE IF NOT EXISTS operational_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Artifacts
        await db.execute('''
        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY,
            task_id INTEGER,
            workflow_id TEXT,
            project_name TEXT,
            artifact_type TEXT,
            file_path TEXT NOT NULL,
            size_bytes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Workflow Policies
        await db.execute('''
        CREATE TABLE IF NOT EXISTS workflow_policies (
            id TEXT PRIMARY KEY,
            project_name TEXT,
            max_attempts INTEGER DEFAULT 3,
            verification_required BOOLEAN DEFAULT 1,
            allowed_agents TEXT
        )''')
        await db.commit()
        print("V1.3.100 DB Migrations complete.")

if __name__ == "__main__":
    asyncio.run(run_v1_3_100_migrations())
