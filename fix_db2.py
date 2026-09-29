import asyncio, sys, aiosqlite
sys.path.insert(0, '.')
from sara.database.core import get_db

async def fix():
    try:
        async with get_db() as db:
            await db.execute('ALTER TABLE tasks ADD COLUMN verification_cmd TEXT')
            await db.execute('ALTER TABLE tasks ADD COLUMN verification_attempts INTEGER DEFAULT 0')
            await db.commit()
    except Exception as e:
        print(e)
asyncio.run(fix())
