import uuid
import datetime
from typing import List, Dict
from sara.database.core import get_db

class TrustLevel:
    SYSTEM_POLICY = 100
    PROJECT_RULE = 90
    VERIFIED_FACT = 80
    USER_PREFERENCE = 70
    RECENT_EVENT = 50
    AGENT_CLAIM = 10

class MemoryStore:
    """Project Knowledge Base and Context Retrieval."""
    
    @staticmethod
    async def store(project: str, content: str, trust_level: str, ttl_days: int = 30) -> str:
        mem_id = str(uuid.uuid4())
        expires = datetime.datetime.now() + datetime.timedelta(days=ttl_days)
        
        async with get_db() as db:
            await db.execute(
                "INSERT INTO memory_store (id, project, content, trust_level, expires_at) VALUES (?, ?, ?, ?, ?)",
                (mem_id, project, content, trust_level, expires.isoformat())
            )
            await db.commit()
        return mem_id

    @staticmethod
    async def retrieve_context(project: str, max_bytes: int = 5000) -> List[Dict]:
        async with get_db() as db:
            async with db.execute(
                "SELECT id, content, trust_level FROM memory_store WHERE project=? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP) ORDER BY created_at DESC",
                (project,)
            ) as c:
                rows = await c.fetchall()
                
        context = []
        current_bytes = 0
        for r in rows:
            size = len(r[1].encode('utf-8'))
            if current_bytes + size > max_bytes:
                break
            context.append({"id": r[0], "content": r[1], "trust_level": r[2]})
            current_bytes += size
            
        return context
