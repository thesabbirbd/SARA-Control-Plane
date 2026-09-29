from sara.database.core import get_db

class ChaosEngine:
    """Failure Injection Framework."""
    
    @staticmethod
    async def inject_failure(target_component: str, failure_type: str):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO chaos_injections (target_component, failure_type) VALUES (?, ?)",
                (target_component, failure_type)
            )
            await db.commit()
            
    @staticmethod
    async def should_fail(component: str) -> bool:
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM chaos_injections WHERE target_component = ? AND active = 1",
                (component,)
            ) as c:
                row = await c.fetchone()
                if row:
                    # Deactivate after firing once to avoid infinite test loop
                    await db.execute("UPDATE chaos_injections SET active = 0 WHERE id = ?", (row[0],))
                    await db.commit()
                    return True
        return False
