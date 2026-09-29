import asyncio
from sara.database.core import get_db

async def run_v1_4_50_migrations():
    async with get_db() as db:
        # Section A: Supervisor Core
        await db.execute('''
        CREATE TABLE IF NOT EXISTS objectives (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            description TEXT,
            constraints TEXT,
            priority INTEGER DEFAULT 0,
            deadline TIMESTAMP,
            status TEXT DEFAULT 'RECEIVED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id TEXT PRIMARY KEY,
            objective_id TEXT NOT NULL,
            tasks TEXT, -- JSON serialization of task graph
            status TEXT,
            current_node TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(objective_id) REFERENCES objectives(id)
        )''')

        # Section B: Multi-Agent System
        await db.execute('''
        CREATE TABLE IF NOT EXISTS agent_capabilities (
            provider TEXT,
            agent_name TEXT,
            roles TEXT, -- e.g. CODER,TESTER,REVIEWER
            capabilities TEXT,
            PRIMARY KEY(provider, agent_name)
        )''')

        # Section C: Intelligent Context & Memory
        await db.execute('''
        CREATE TABLE IF NOT EXISTS memory_store (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            content TEXT,
            trust_level TEXT, -- SYSTEM_POLICY, PROJECT_RULE, VERIFIED_FACT, etc.
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Section D: Deployment + Environment Orchestration
        await db.execute('''
        CREATE TABLE IF NOT EXISTS deployment_targets (
            id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            name TEXT NOT NULL,
            environment TEXT NOT NULL, -- dev, staging, prod
            host TEXT,
            policy TEXT
        )''')

        await db.execute('''
        CREATE TABLE IF NOT EXISTS deployments (
            id TEXT PRIMARY KEY,
            target_id TEXT NOT NULL,
            version TEXT,
            status TEXT, -- PENDING, DEPLOYED, ROLLBACK
            health TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(target_id) REFERENCES deployment_targets(id)
        )''')

        # Section E: Worker Metrics
        await db.execute('''
        CREATE TABLE IF NOT EXISTS worker_metrics (
            worker_id TEXT PRIMARY KEY,
            cpu_usage REAL,
            ram_usage REAL,
            active_tasks INTEGER,
            last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        await db.commit()
        print("V1.4.50 Migrations Complete")

if __name__ == "__main__":
    asyncio.run(run_v1_4_50_migrations())
