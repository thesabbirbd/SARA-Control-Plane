import pytest
import asyncio
from unittest.mock import patch, MagicMock
from sara.github.orchestrator import PROrchestrator
from sara.integrations.coderabbit import CodeRabbitIntegration
from sara.integrations.sonar import SonarIntegration
from sara.integrations.dependabot import DependabotIntegration

@pytest.mark.asyncio
async def test_pr_writer_lock():
    # Setup test DB safely if needed, but we can rely on standard testing practice.
    # We will just test the lock mechanism logic.
    repo = "test/repo"
    pr = 101
    
    # 1. Jules gets the lock
    success1 = await PROrchestrator.acquire_lock(repo, pr, "Jules", "exec-1")
    assert success1 is True
    
    # 2. CodeRabbit tries to get the lock (should fail, ONE WRITER POLICY)
    success2 = await PROrchestrator.acquire_lock(repo, pr, "CodeRabbit", "exec-2")
    assert success2 is False
    
    # 3. Jules releases lock
    await PROrchestrator.release_lock(repo, pr, "Jules")
    
    # 4. Now CodeRabbit can get the lock
    success3 = await PROrchestrator.acquire_lock(repo, pr, "CodeRabbit", "exec-2")
    assert success3 is True

def test_coderabbit_filter():
    finding = {"severity": "CRITICAL", "message": "SQL Injection"}
    res = CodeRabbitIntegration.filter_finding(finding)
    assert res["action"] == "BLOCK_MERGE"
    
    finding2 = {"severity": "MINOR", "message": "Typo"}
    res2 = CodeRabbitIntegration.filter_finding(finding2)
    assert res2["action"] == "COMMENT_ONLY"

def test_sonar_gate():
    assert SonarIntegration.evaluate_gate("OK") == "PASSED"
    assert SonarIntegration.evaluate_gate("UNKNOWN") == "UNKNOWN"

def test_dependabot_routing():
    res = DependabotIntegration.process_failure("org/repo", 55, "tests failed")
    assert res["action"] == "ROUTE_TO_JULES"

@pytest.mark.asyncio
async def test_finding_deduplication():
    repo = "test/dedup"
    pr = 99
    
    await PROrchestrator.add_finding(repo, pr, "Sonar", "HIGH", "Memory Leak", "main.py", 10)
    # Adding the exact same finding should not crash or duplicate
    await PROrchestrator.add_finding(repo, pr, "CodeRabbit", "HIGH", "Memory Leak", "main.py", 10)

    # In a real test, we would query DB and assert count == 1, but we rely on the internal logic for now.
    from sara.database.core import get_db
    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) FROM github_findings WHERE repo_full_name=? AND pr_number=?", (repo, pr)) as c:
            count = (await c.fetchone())[0]
            # Will be 1 due to the deduplication block in add_finding
            assert count == 1
