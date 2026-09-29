from sara.database.core import get_db

class FleetJournal:
    @staticmethod
    async def log_operation(operation: str, repo: str, before: str, after: str, result: str, actor: str):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO fleet_journal (operation, repo_full_name, before_state, after_state, result, actor) VALUES (?, ?, ?, ?, ?, ?)",
                (operation, repo, before, after, result, actor)
            )
            await db.commit()
            
    @staticmethod
    async def check_anomaly(repo: str) -> str:
        # Example anomaly detection logic
        # e.g., Dependabot PR storm, CI failing repeatedly
        async with get_db() as db:
            # Check for excessive PRs in the last hour
            async with db.execute("SELECT COUNT(*) FROM ci_failures WHERE repo_full_name = ? AND repair_cycle > 2", (repo,)) as c:
                count = (await c.fetchone())[0]
                if count > 5:
                    return "ANOMALY_CI_STORM"
        return "NORMAL"
