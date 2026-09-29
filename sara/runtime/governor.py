from typing import Dict
from sara.database.core import get_db

class AutonomyGovernor:
    """Enforces global autonomy limits preventing runaway AI execution."""
    
    MAX_REPAIR_CYCLES = 3
    MAX_CONCURRENT_WRITERS = 1
    MAX_WORKFLOW_RUNTIME_MINUTES = 240
    
    @classmethod
    def check_repair_cycle(cls, current_cycle: int) -> bool:
        return current_cycle <= cls.MAX_REPAIR_CYCLES

class WorkerDispatcher:
    """Resource-aware Worker Dispatch."""
    
    @staticmethod
    async def get_least_loaded_worker(required_cap: str) -> str:
        async with get_db() as db:
            query = """
            SELECT rw.worker_id, wm.cpu_usage, wm.ram_usage 
            FROM remote_workers rw
            LEFT JOIN worker_metrics wm ON rw.worker_id = wm.worker_id
            WHERE rw.status = 'ONLINE' AND rw.capabilities LIKE ?
            ORDER BY COALESCE(wm.cpu_usage, 0) ASC
            LIMIT 1
            """
            async with db.execute(query, (f"%{required_cap}%",)) as c:
                row = await c.fetchone()
                if row:
                    return row[0]
        return None
