import json
import uuid
from typing import Dict, Any
from sara.database.core import get_db

class EventBus:
    """Durable internal event backbone for observability and loose coupling."""
    
    @staticmethod
    async def publish(event_type: str, correlation_id: str, payload: Dict[str, Any]):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO system_events (correlation_id, event_type, payload) VALUES (?, ?, ?)",
                (correlation_id, event_type, json.dumps(payload))
            )
            await db.commit()
            
    @staticmethod
    async def get_history(correlation_id: str):
        async with get_db() as db:
            async with db.execute(
                "SELECT event_type, payload, timestamp FROM system_events WHERE correlation_id = ? ORDER BY timestamp ASC",
                (correlation_id,)
            ) as c:
                return await c.fetchall()
