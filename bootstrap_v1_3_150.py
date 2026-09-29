import os, sys, asyncio

def setup_dirs():
    dirs = [
        "sara/github",
        "sara/integrations",
        "docs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

async def run_db_migrations():
    sys.path.insert(0, os.path.abspath("."))
    from sara.database.core import get_db
    async with get_db() as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS github_repos (
            id INTEGER PRIMARY KEY,
            full_name TEXT UNIQUE NOT NULL,
            visibility TEXT,
            default_branch TEXT,
            language TEXT,
            has_actions BOOLEAN DEFAULT 0,
            has_dependabot BOOLEAN DEFAULT 0,
            has_sonar BOOLEAN DEFAULT 0,
            has_coderabbit BOOLEAN DEFAULT 0,
            has_jules BOOLEAN DEFAULT 0,
            updated_at TIMESTAMP
        )''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS github_prs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            pr_number INTEGER NOT NULL,
            state TEXT NOT NULL,
            writer_lock TEXT,
            writer_execution_id TEXT,
            lock_timestamp TIMESTAMP,
            UNIQUE(repo_full_name, pr_number)
        )''')

        await db.execute('''
        CREATE TABLE IF NOT EXISTS github_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_full_name TEXT NOT NULL,
            pr_number INTEGER,
            source TEXT NOT NULL,
            severity TEXT,
            file_path TEXT,
            line INTEGER,
            description TEXT,
            status TEXT DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS jules_sessions (
            id TEXT PRIMARY KEY,
            repo_full_name TEXT NOT NULL,
            branch TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        await db.commit()
        print("V1.3.150 DB Migrations complete.")

if __name__ == "__main__":
    setup_dirs()
    asyncio.run(run_db_migrations())
