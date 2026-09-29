import asyncio
from sara.database.core import get_db

async def run_v1_5_50_migrations():
    async with get_db() as db:
        # 1. Event Backbone
        await db.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlation_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # 2. DAG Execution Engine
        await db.execute('''
        CREATE TABLE IF NOT EXISTS dag_nodes (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            dependencies TEXT, -- comma-separated node ids
            input_context TEXT,
            output_context TEXT,
            agent_role TEXT,
            worker_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # 3. Environment & Target Definitions
        await db.execute('''
        CREATE TABLE IF NOT EXISTS environments (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            policy TEXT
        )''')
        
        # Deployments table update for multi-env transactions
        await db.execute('''
        CREATE TABLE IF NOT EXISTS deployment_transactions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            environment_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            status TEXT DEFAULT 'PREPARE',
            health_status TEXT,
            rollback_status TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )''')
        
        # 4. Chaos & Failure Injection
        await db.execute('''
        CREATE TABLE IF NOT EXISTS chaos_injections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_component TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        await db.commit()
        print("V1.5.50 Migrations Complete")

if __name__ == "__main__":
    asyncio.run(run_v1_5_50_migrations())
