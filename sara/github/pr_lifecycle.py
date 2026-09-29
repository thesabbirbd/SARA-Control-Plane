from typing import Dict, List
from sara.database.core import get_db

class PRLifecycle:
    """Manages PR Check Aggregation, Timelines, and Conflict Detection."""
    
    @staticmethod
    async def aggregate_checks(repo: str, pr: int, checks: List[Dict]) -> str:
        # checks = [{"name": "CI", "status": "PASS"}, {"name": "Sonar", "status": "UNKNOWN"}]
        has_fail = any(c['status'] == 'FAIL' for c in checks)
        has_unknown = any(c['status'] == 'UNKNOWN' for c in checks)
        
        if has_fail:
            return "NEEDS_FIX"
        if has_unknown:
            return "WAITING_PROVIDER"
        return "READY_FOR_HUMAN"

    @staticmethod
    async def log_event(repo: str, pr: int, event_type: str, details: str):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO pr_events (repo_full_name, pr_number, event_type, details) VALUES (?, ?, ?, ?)",
                (repo, pr, event_type, details)
            )
            await db.commit()

