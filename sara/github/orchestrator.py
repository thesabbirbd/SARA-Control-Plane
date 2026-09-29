from typing import Optional, Dict
from sara.database.core import get_db

class PROrchestrator:
    """Enforces ONE PR = ONE PRIMARY CODING WRITER policy."""
    
    @staticmethod
    async def acquire_lock(repo: str, pr_number: int, writer_name: str, execution_id: str) -> bool:
        async with get_db() as db:
            async with db.execute("SELECT writer_lock FROM github_prs WHERE repo_full_name=? AND pr_number=?", (repo, pr_number)) as c:
                row = await c.fetchone()
            
            if row:
                current_writer = row[0]
                if current_writer and current_writer != writer_name:
                    return False # Locked by someone else
                
                await db.execute(
                    "UPDATE github_prs SET writer_lock=?, writer_execution_id=?, lock_timestamp=CURRENT_TIMESTAMP WHERE repo_full_name=? AND pr_number=?",
                    (writer_name, execution_id, repo, pr_number)
                )
            else:
                await db.execute(
                    "INSERT INTO github_prs (repo_full_name, pr_number, state, writer_lock, writer_execution_id, lock_timestamp) VALUES (?, ?, 'OPEN', ?, ?, CURRENT_TIMESTAMP)",
                    (repo, pr_number, writer_name, execution_id)
                )
            await db.commit()
            return True

    @staticmethod
    async def release_lock(repo: str, pr_number: int, writer_name: str) -> bool:
        async with get_db() as db:
            await db.execute(
                "UPDATE github_prs SET writer_lock=NULL, writer_execution_id=NULL WHERE repo_full_name=? AND pr_number=? AND writer_lock=?",
                (repo, pr_number, writer_name)
            )
            await db.commit()
            return True

    @staticmethod
    async def add_finding(repo: str, pr_number: int, source: str, severity: str, desc: str, file_path: str = None, line: int = None):
        """Adds a finding, normalizing and deduplicating."""
        async with get_db() as db:
            # Simple deduplication check
            async with db.execute("SELECT id FROM github_findings WHERE repo_full_name=? AND pr_number=? AND description=? AND file_path=? AND line=?",
                                  (repo, pr_number, desc, file_path, line)) as c:
                if await c.fetchone():
                    return # Deduplicated
            
            await db.execute(
                "INSERT INTO github_findings (repo_full_name, pr_number, source, severity, description, file_path, line) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (repo, pr_number, source, severity, desc, file_path, line)
            )
            await db.commit()
