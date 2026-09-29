from sara.database.core import get_db

async def run_migrations():
    async with get_db() as db:
        # Existing tables
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                chat_id INTEGER,
                message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pid INTEGER,
                log_path TEXT,
                result TEXT,
                parent_task_id INTEGER,
                retry_count INTEGER DEFAULT 0,
                next_attempt TIMESTAMP,
                priority TEXT DEFAULT 'normal',
                schedule_time TIMESTAMP,
                depends_on INTEGER,
                telemetry TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                active_project TEXT,
                notify_enabled INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # New Domain Models V1.3
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                attempt INTEGER DEFAULT 1,
                provider TEXT DEFAULT 'antigravity',
                session_id TEXT,
                pid INTEGER,
                status TEXT DEFAULT 'STARTING',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP,
                telemetry TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                project_name TEXT,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE',
                metadata TEXT
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS task_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT,
                task_id INTEGER NOT NULL,
                depends_on_task_id INTEGER NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(depends_on_task_id) REFERENCES tasks(id)
            )
        ''')

        await db.commit()
