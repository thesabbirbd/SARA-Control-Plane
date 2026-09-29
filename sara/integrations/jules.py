import uuid
from sara.database.core import get_db

class JulesProvider:
    """Jules Asynchronous Coding Agent integration."""
    @staticmethod
    async def create_task(repo: str, instruction: str) -> str:
        session_id = str(uuid.uuid4())
        async with get_db() as db:
            await db.execute(
                "INSERT INTO jules_sessions (id, repo_full_name, branch, status) VALUES (?, ?, ?, ?)",
                (session_id, repo, f"jules/repair-{session_id[:8]}", "PENDING")
            )
            await db.commit()
        return session_id
