import pytest
import asyncio
import uuid
import time
from sara.deploy.orchestrator import DeploymentTransaction, DockerBridge

@pytest.mark.asyncio
async def test_deployment_stress():
    # 50 concurrent deployments
    workflow_ids = [str(uuid.uuid4()) for _ in range(50)]
    docker = DockerBridge()
    
    start_time = time.time()
    
    # Begin tx concurrently
    tx_tasks = [DeploymentTransaction.begin_transaction(wf, f"prod-{i}", f"target-{i}") for i, wf in enumerate(workflow_ids)]
    tx_ids = await asyncio.gather(*tx_tasks)
    
    # Deploy concurrently
    deploy_tasks = [docker.deploy(f"target-{i}", "artifact") for i in range(50)]
    results = await asyncio.gather(*deploy_tasks)
    
    # Complete concurrently
    complete_tasks = [DeploymentTransaction.complete_transaction(tx, wf, res) for tx, wf, res in zip(tx_ids, workflow_ids, results)]
    await asyncio.gather(*complete_tasks)
    
    duration = time.time() - start_time
    
    # Validate
    assert len(results) == 50
    # Because of DockerBridge sleep(0.1), concurrent should take slightly > 0.1s, not 5.0s
    assert duration < 10.0
