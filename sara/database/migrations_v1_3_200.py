import asyncio
from sara.database.core import get_db

async def run_v1_3_200_migrations():
    async with get_db() as db:
        # CI/CD Intelligence
        await db.execute('''
        CREATE TABLE IF NOT EXISTS ci_workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            name TEXT,
            file_path TEXT,
            trigger TEXT,
            status TEXT,
            last_run TIMESTAMP
        )''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS ci_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            pr_number INTEGER,
            workflow TEXT,
            classification TEXT,
            signature TEXT,
            repair_task_id TEXT,
            repair_cycle INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # PR Lifecycle tracking extensions
        # We will add columns to github_prs if needed, or track timeline in a new table
        await db.execute('''
        CREATE TABLE IF NOT EXISTS pr_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            pr_number INTEGER,
            event_type TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Issue Triage
        await db.execute('''
        CREATE TABLE IF NOT EXISTS github_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            issue_number INTEGER NOT NULL,
            classification TEXT,
            priority INTEGER DEFAULT 0,
            state TEXT,
            assigned_task TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(repo_full_name, issue_number)
        )''')

        # Release Engineering
        await db.execute('''
        CREATE TABLE IF NOT EXISTS project_releases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            version TEXT NOT NULL,
            strategy TEXT,
            status TEXT,
            rollback_meta TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Remote Workers
        await db.execute('''
        CREATE TABLE IF NOT EXISTS remote_workers (
            worker_id TEXT PRIMARY KEY,
            hostname TEXT,
            os_info TEXT,
            capabilities TEXT,
            status TEXT,
            last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Fleet Actions Journal
        await db.execute('''
        CREATE TABLE IF NOT EXISTS fleet_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT,
            repo_full_name TEXT,
            before_state TEXT,
            after_state TEXT,
            result TEXT,
            actor TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        await db.commit()
        print("V1.3.200 Migrations Complete")

if __name__ == "__main__":
    asyncio.run(run_v1_3_200_migrations())
