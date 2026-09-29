import pytest
import asyncio
from sara.github.ci_intelligence import CIIntelligence
from sara.github.pr_lifecycle import PRLifecycle
from sara.github.issues import IssueTriage
from sara.github.releases import ReleaseEngine

@pytest.mark.asyncio
async def test_ci_intelligence():
    import uuid
    repo = f"test/ci_repo-{uuid.uuid4()}"
    pr = 1
    
    # 1. Classification
    cls = CIIntelligence.classify_failure("AssertionError: expected true but got false")
    assert cls == "TEST_FAILURE"
    
    # 2. Repair loop governor
    log = "Failure in module X"
    res1 = await CIIntelligence.evaluate_repair(repo, pr, "test-flow", log)
    assert res1["action"] == "REPAIR"
    assert res1["cycle"] == 1
    
    res2 = await CIIntelligence.evaluate_repair(repo, pr, "test-flow", log)
    assert res2["action"] == "REPAIR"
    assert res2["cycle"] == 2
    
    res3 = await CIIntelligence.evaluate_repair(repo, pr, "test-flow", log)
    assert res3["action"] == "REPAIR"
    assert res3["cycle"] == 3
    
    # Exceeding limit
    res4 = await CIIntelligence.evaluate_repair(repo, pr, "test-flow", log)
    assert res4["action"] == "BLOCK"
    assert res4["reason"] == "MAX_REPAIR_CYCLES_REACHED"

@pytest.mark.asyncio
async def test_pr_lifecycle():
    checks = [
        {"name": "CI", "status": "PASS"},
        {"name": "Sonar", "status": "PASS"}
    ]
    state = await PRLifecycle.aggregate_checks("repo", 1, checks)
    assert state == "READY_FOR_HUMAN"
    
    checks.append({"name": "CodeRabbit", "status": "FAIL"})
    state2 = await PRLifecycle.aggregate_checks("repo", 1, checks)
    assert state2 == "NEEDS_FIX"
    
    await PRLifecycle.log_event("repo", 1, "REVIEW", "CodeRabbit finished")

@pytest.mark.asyncio
async def test_issue_triage():
    cls = IssueTriage.classify("Fix login bug", "User cannot login", ["bug"])
    assert cls == "BUG"
    
    prio = IssueTriage.calculate_priority(cls, 5) # 5 days old
    assert prio == 55 # 50 (BUG) + 5
    
    await IssueTriage.register_issue("repo", 99, "Security vulnerability", "SQL injection", ["CVE"], 1)
    
def test_release_engine():
    commits = [
        {"message": "feat: added login"},
        {"message": "fix: resolved crash"}
    ]
    cl = ReleaseEngine.generate_changelog(commits)
    assert "## Features" in cl
    assert "feat: added login" in cl
    assert "## Fixes" in cl
    assert "fix: resolved crash" in cl
    
    readiness = ReleaseEngine.check_readiness([{"status": "PASS"}, {"status": "FAIL"}])
    assert readiness is False
    
    readiness2 = ReleaseEngine.check_readiness([{"status": "PASS"}, {"status": "PASS"}])
    assert readiness2 is True
