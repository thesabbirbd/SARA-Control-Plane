import uuid
from typing import Dict
from sara.database.core import get_db

class DeploymentEngine:
    """Orchestrates Environment Deployments, Health Checks, and Rollbacks."""
    
    @staticmethod
    async def register_target(project: str, name: str, environment: str, host: str, policy: str = "REQUIRE_CI") -> str:
        tid = str(uuid.uuid4())
        async with get_db() as db:
            await db.execute(
                "INSERT INTO deployment_targets (id, project, name, environment, host, policy) VALUES (?, ?, ?, ?, ?, ?)",
                (tid, project, name, environment, host, policy)
            )
            await db.commit()
        return tid

    @staticmethod
    async def create_deployment(target_id: str, version: str) -> str:
        dep_id = str(uuid.uuid4())
        async with get_db() as db:
            await db.execute(
                "INSERT INTO deployments (id, target_id, version, status) VALUES (?, ?, ?, 'PENDING')",
                (dep_id, target_id, version)
            )
            await db.commit()
        return dep_id

    @staticmethod
    async def verify_health(dep_id: str, is_healthy: bool):
        async with get_db() as db:
            status = 'DEPLOYED' if is_healthy else 'ROLLBACK'
            await db.execute(
                "UPDATE deployments SET status=?, health=? WHERE id=?",
                (status, "HEALTHY" if is_healthy else "UNHEALTHY", dep_id)
            )
            await db.commit()
