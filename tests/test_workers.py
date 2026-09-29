import pytest
from sara.workers.core import WorkerRegistry

@pytest.mark.asyncio
async def test_worker_registry():
    wid = await WorkerRegistry.register_worker("node-1", "linux", ["docker", "jules"])
    assert wid is not None
    
    workers = await WorkerRegistry.get_available_workers("jules")
    assert len(workers) > 0
    assert any(w["worker_id"] == wid for w in workers)
    
    await WorkerRegistry.drain_worker(wid)
    
    workers_after_drain = await WorkerRegistry.get_available_workers("jules")
    assert not any(w["worker_id"] == wid for w in workers_after_drain)
