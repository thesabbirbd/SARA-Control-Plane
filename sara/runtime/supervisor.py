import uuid
import json
from typing import Dict, List, Optional
from sara.database.core import get_db

class ObjectiveState:
    RECEIVED = "RECEIVED"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    READY = "READY"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    WAITING_HUMAN = "WAITING_HUMAN"

class SupervisorService:
    """Autonomous Supervisor Core for executing high-level objectives."""
    
    @staticmethod
    async def create_objective(project: str, description: str, constraints: str = "") -> str:
        obj_id = str(uuid.uuid4())
        async with get_db() as db:
            await db.execute(
                "INSERT INTO objectives (id, project, description, constraints) VALUES (?, ?, ?, ?)",
                (obj_id, project, description, constraints)
            )
            await db.commit()
        return obj_id

    @staticmethod
    async def advance_state(obj_id: str, new_state: str):
        async with get_db() as db:
            await db.execute(
                "UPDATE objectives SET status = ? WHERE id = ?",
                (new_state, obj_id)
            )
            await db.commit()

    @staticmethod
    async def create_plan(obj_id: str, tasks: List[Dict]) -> str:
        plan_id = str(uuid.uuid4())
        # Basic cycle detection mockup: A real one would build a directed graph and check for cycles
        visited = set()
        for t in tasks:
            if t.get('id') in visited:
                raise ValueError(f"Cycle detected at task {t['id']}")
            visited.add(t.get('id'))
            
        async with get_db() as db:
            await db.execute(
                "INSERT INTO plans (id, objective_id, tasks, status) VALUES (?, ?, ?, ?)",
                (plan_id, obj_id, json.dumps(tasks), "READY")
            )
            await db.commit()
        
        await SupervisorService.advance_state(obj_id, ObjectiveState.PLANNING)
        return plan_id

class MultiAgentRouter:
    """Agent Selection and Single-Writer enforcement."""
    
    @staticmethod
    async def register_agent(provider: str, agent_name: str, roles: List[str], capabilities: List[str]):
        async with get_db() as db:
            await db.execute(
                "INSERT OR REPLACE INTO agent_capabilities (provider, agent_name, roles, capabilities) VALUES (?, ?, ?, ?)",
                (provider, agent_name, ",".join(roles), ",".join(capabilities))
            )
            await db.commit()

    @staticmethod
    async def select_agent(role: str, required_caps: List[str]) -> Optional[Dict]:
        async with get_db() as db:
            async with db.execute("SELECT provider, agent_name, roles, capabilities FROM agent_capabilities") as c:
                agents = await c.fetchall()
                
        for row in agents:
            roles = row[2].split(",")
            caps = row[3].split(",")
            if role in roles:
                if all(c in caps for c in required_caps):
                    return {"provider": row[0], "agent": row[1]}
        return None
