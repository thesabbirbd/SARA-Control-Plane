from typing import Dict, List
import uuid
from sara.database.core import get_db

class WorkerRegistry:
    """Remote Worker registration and routing engine."""
    
    @staticmethod
    async def register_worker(hostname: str, os_info: str, capabilities: List[str]) -> str:
        worker_id = str(uuid.uuid4())
        caps = ",".join(capabilities)
        async with get_db() as db:
            await db.execute(
                "INSERT INTO remote_workers (worker_id, hostname, os_info, capabilities, status) VALUES (?, ?, ?, ?, 'ONLINE')",
                (worker_id, hostname, os_info, caps)
            )
            await db.commit()
        return worker_id
        
    @staticmethod
    async def drain_worker(worker_id: str):
        async with get_db() as db:
            await db.execute(
                "UPDATE remote_workers SET status = 'DRAINING' WHERE worker_id = ?",
                (worker_id,)
            )
            await db.commit()

    @staticmethod
    async def get_available_workers(required_cap: str = None) -> List[Dict]:
        async with get_db() as db:
            query = "SELECT worker_id, capabilities FROM remote_workers WHERE status = 'ONLINE'"
            async with db.execute(query) as c:
                rows = await c.fetchall()
                
            available = []
            for r in rows:
                caps = r[1].split(",") if r[1] else []
                if required_cap is None or required_cap in caps:
                    available.append({"worker_id": r[0], "capabilities": caps})
            return available
