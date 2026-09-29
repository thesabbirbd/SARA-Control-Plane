import json
import asyncio
from sara.database.core import get_db

_subscribers = []

def subscribe(callback):
    """Callback should be an async function accepting (entity_type, entity_id, event_type, payload)"""
    _subscribers.append(callback)

async def publish_event(entity_type: str, entity_id: str, event_type: str, payload: dict = None):
    # Persist
    async with get_db() as db:
        await db.execute(
            "INSERT INTO events (entity_type, entity_id, event_type, payload) VALUES (?, ?, ?, ?)",
            (entity_type, str(entity_id), event_type, json.dumps(payload or {}))
        )
        await db.commit()
    
    # Notify subscribers
    for sub in _subscribers:
        try:
            await sub(entity_type, entity_id, event_type, payload)
        except Exception as e:
            print(f"Event subscriber error: {e}")

