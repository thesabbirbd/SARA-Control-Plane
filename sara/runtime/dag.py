import uuid
import json
from typing import List, Dict, Set
from sara.database.core import get_db
from sara.core.events import EventBus

class DAGNodeState:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"

class DAGEngine:
    """Dependency-aware execution engine."""
    
    @staticmethod
    async def create_graph(workflow_id: str, nodes_def: List[Dict]):
        async with get_db() as db:
            for n in nodes_def:
                nid = n.get('id', str(uuid.uuid4()))
                deps = ",".join(n.get('dependencies', []))
                await db.execute(
                    "INSERT INTO dag_nodes (id, workflow_id, name, dependencies, agent_role) VALUES (?, ?, ?, ?, ?)",
                    (nid, workflow_id, n['name'], deps, n.get('role', 'CODER'))
                )
            await db.commit()
            
    @staticmethod
    async def get_runnable_nodes(workflow_id: str) -> List[Dict]:
        async with get_db() as db:
            async with db.execute("SELECT id, name, dependencies, status FROM dag_nodes WHERE workflow_id = ?", (workflow_id,)) as c:
                all_nodes = await c.fetchall()
                
        # Find pending nodes where all dependencies are COMPLETED
        completed = {r[0] for r in all_nodes if r[3] == DAGNodeState.COMPLETED}
        runnable = []
        for r in all_nodes:
            if r[3] == DAGNodeState.PENDING:
                deps = r[2].split(",") if r[2] else []
                if all(d in completed for d in deps):
                    runnable.append({"id": r[0], "name": r[1]})
        return runnable

    @staticmethod
    async def update_node_state(node_id: str, state: str, workflow_id: str):
        async with get_db() as db:
            await db.execute("UPDATE dag_nodes SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (state, node_id))
            await db.commit()
        await EventBus.publish("dag.node_updated", workflow_id, {"node_id": node_id, "state": state})
