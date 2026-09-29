import pytest
import asyncio
import uuid
from sara.core.events import EventBus
from sara.core.state import StateMachine, WorkflowState
from sara.runtime.dag import DAGEngine, DAGNodeState
from sara.deploy.orchestrator import DeploymentTransaction, SSHBridge, DockerBridge
from sara.core.chaos import ChaosEngine

@pytest.mark.asyncio
async def test_end_to_end_north_star():
    # Correlation ID
    workflow_id = str(uuid.uuid4())
    
    # 1. State Machine transition
    await StateMachine.transition(workflow_id, WorkflowState.RECEIVED, "User requested")
    await StateMachine.transition(workflow_id, WorkflowState.PLANNING, "Decomposing objective")
    
    # 2. DAG Engine Execution
    nodes = [
        {"id": "A-" + workflow_id, "name": "Recon", "role": "PLANNER", "dependencies": []},
        {"id": "B-" + workflow_id, "name": "Code", "role": "CODER", "dependencies": ["A-" + workflow_id]},
        {"id": "C-" + workflow_id, "name": "Test", "role": "TESTER", "dependencies": ["B-" + workflow_id]}
    ]
    await DAGEngine.create_graph(workflow_id, nodes)
    
    # Node A is runnable
    runnable_1 = await DAGEngine.get_runnable_nodes(workflow_id)
    assert len(runnable_1) == 1
    assert runnable_1[0]["id"] == "A-" + workflow_id
    
    # Complete A
    await DAGEngine.update_node_state("A-" + workflow_id, DAGNodeState.COMPLETED, workflow_id)
    
    # Node B is runnable
    runnable_2 = await DAGEngine.get_runnable_nodes(workflow_id)
    assert len(runnable_2) == 1
    assert runnable_2[0]["id"] == "B-" + workflow_id
    
    # Complete B and C
    await DAGEngine.update_node_state("B-" + workflow_id, DAGNodeState.COMPLETED, workflow_id)
    await DAGEngine.update_node_state("C-" + workflow_id, DAGNodeState.COMPLETED, workflow_id)
    
    # Check runnable is empty
    runnable_3 = await DAGEngine.get_runnable_nodes(workflow_id)
    assert len(runnable_3) == 0
    
    # 3. Chaos Injection
    await ChaosEngine.inject_failure("SSHBridge", "NETWORK_TIMEOUT")
    
    # 4. Deployment Transaction
    env_id = "staging-01"
    target_id = "ssh-host-1"
    tx_id = await DeploymentTransaction.begin_transaction(workflow_id, env_id, target_id)
    
    ssh = SSHBridge()
    success = await ssh.deploy("ssh-host-1", "artifact.tar.gz")
    assert success is False # Because chaos was injected!
    
    await DeploymentTransaction.complete_transaction(tx_id, workflow_id, success)
    
    # 5. Recovery/Rollback Execution Path
    if not success:
        await StateMachine.transition(workflow_id, WorkflowState.ROLLING_BACK, "SSH deployment failed")
        
    # 6. Event Log Verification
    events = await EventBus.get_history(workflow_id)
    event_types = [e[0] for e in events]
    assert "workflow.state_changed" in event_types
    assert "dag.node_updated" in event_types
    assert "deployment.started" in event_types
    assert "deployment.failed" in event_types

@pytest.mark.asyncio
async def test_concurrent_deployments_docker():
    workflow_id = str(uuid.uuid4())
    docker = DockerBridge()
    
    t1 = DeploymentTransaction.begin_transaction(workflow_id, "prod-1", "docker-1")
    t2 = DeploymentTransaction.begin_transaction(workflow_id, "prod-2", "docker-2")
    
    tx1, tx2 = await asyncio.gather(t1, t2)
    
    d1 = docker.deploy("docker-1", "artifact")
    d2 = docker.deploy("docker-2", "artifact")
    
    res1, res2 = await asyncio.gather(d1, d2)
    assert res1 is True
    assert res2 is True
    
    c1 = DeploymentTransaction.complete_transaction(tx1, workflow_id, res1)
    c2 = DeploymentTransaction.complete_transaction(tx2, workflow_id, res2)
    await asyncio.gather(c1, c2)
