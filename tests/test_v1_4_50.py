import uuid
import pytest
import asyncio
from sara.runtime.supervisor import SupervisorService, MultiAgentRouter, ObjectiveState
from sara.runtime.memory import MemoryStore, TrustLevel
from sara.runtime.deployment import DeploymentEngine
from sara.runtime.governor import AutonomyGovernor, WorkerDispatcher
from sara.workers.core import WorkerRegistry

@pytest.mark.asyncio
async def test_supervisor_core():
    # 1. Objective Creation
    obj_id = await SupervisorService.create_objective("portfolio", "Add responsive navbar", "no downtime")
    assert obj_id is not None
    
    # 2. Plan Creation
    tasks = [{"id": "t1", "desc": "write code"}, {"id": "t2", "desc": "write tests"}]
    plan_id = await SupervisorService.create_plan(obj_id, tasks)
    assert plan_id is not None
    
    # 3. Cycle Detection (Validation)
    with pytest.raises(ValueError):
        await SupervisorService.create_plan(obj_id, [{"id": "t1"}, {"id": "t1"}])

@pytest.mark.asyncio
async def test_multi_agent_system():
    await MultiAgentRouter.register_agent("gemini", "gemini-pro", ["CODER", "REVIEWER"], ["python", "javascript"])
    
    # Select Coder
    agent = await MultiAgentRouter.select_agent("CODER", ["python"])
    assert agent is not None
    assert agent["provider"] == "gemini"
    
    # Missing capability
    agent_fail = await MultiAgentRouter.select_agent("CODER", ["rust"])
    assert agent_fail is None

@pytest.mark.asyncio
async def test_memory_context():
    mem_id = await MemoryStore.store("portfolio", "Use Next.js app router.", "PROJECT_RULE")
    assert mem_id is not None
    
    ctx = await MemoryStore.retrieve_context("portfolio", max_bytes=5000)
    assert len(ctx) >= 1
    assert any(c["content"] == "Use Next.js app router." for c in ctx)

@pytest.mark.asyncio
async def test_deployment_orchestration():
    tid = await DeploymentEngine.register_target("portfolio", "prod-1", "production", "ssh://server")
    dep_id = await DeploymentEngine.create_deployment(tid, "v1.4.0")
    
    # Simulate health failure -> rollback
    await DeploymentEngine.verify_health(dep_id, is_healthy=False)
    
    from sara.database.core import get_db
    async with get_db() as db:
        async with db.execute("SELECT status, health FROM deployments WHERE id=?", (dep_id,)) as c:
            row = await c.fetchone()
            assert row[0] == "ROLLBACK"
            assert row[1] == "UNHEALTHY"

@pytest.mark.asyncio
async def test_worker_load_balancer():
    # Register a worker with some capabilities
    cap = f"agy-{uuid.uuid4()}"
    wid = await WorkerRegistry.register_worker("node-load", "linux", ["docker", cap])
    
    # Inject fake metrics
    from sara.database.core import get_db
    async with get_db() as db:
        await db.execute(
            "INSERT INTO worker_metrics (worker_id, cpu_usage, ram_usage, active_tasks) VALUES (?, 10.5, 40.0, 1)",
            (wid,)
        )
        await db.commit()
        
    best_worker = await WorkerDispatcher.get_least_loaded_worker(cap)
    assert best_worker == wid
