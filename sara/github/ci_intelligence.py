import hashlib
from typing import Dict, Optional
from sara.database.core import get_db

class CIIntelligence:
    """Handles CI discovery, failure classification, signatures, and loop governors."""
    
    @staticmethod
    def classify_failure(log_evidence: str) -> str:
        log = log_evidence.lower()
        if "test failed" in log or "assertionerror" in log:
            return "TEST_FAILURE"
        elif "build failed" in log or "compilation error" in log:
            return "BUILD_FAILURE"
        elif "lint" in log or "flake8" in log or "eslint" in log:
            return "LINT_FAILURE"
        return "UNKNOWN"

    @staticmethod
    def generate_signature(repo: str, workflow: str, log_evidence: str) -> str:
        # Strip out timestamps, hashes, etc. to make it stable.
        # Simplistic hash for demonstration.
        core_err = log_evidence.split("\\n")[-1] if "\\n" in log_evidence else log_evidence
        raw = f"{repo}:{workflow}:{core_err}".encode('utf-8')
        return hashlib.md5(raw).hexdigest()

    @classmethod
    async def evaluate_repair(cls, repo: str, pr: int, workflow: str, log_evidence: str, max_cycles: int = 3) -> Dict:
        classification = cls.classify_failure(log_evidence)
        signature = cls.generate_signature(repo, workflow, log_evidence)
        
        async with get_db() as db:
            async with db.execute(
                "SELECT id, repair_cycle FROM ci_failures WHERE repo_full_name=? AND pr_number=? AND signature=?",
                (repo, pr, signature)
            ) as c:
                row = await c.fetchone()
                
            if row:
                cycle = row[1]
                if cycle >= max_cycles:
                    return {"action": "BLOCK", "reason": "MAX_REPAIR_CYCLES_REACHED", "signature": signature}
                
                # Increment cycle
                await db.execute(
                    "UPDATE ci_failures SET repair_cycle = repair_cycle + 1 WHERE id=?",
                    (row[0],)
                )
                await db.commit()
                return {"action": "REPAIR", "signature": signature, "cycle": cycle + 1, "classification": classification}
            
            else:
                await db.execute(
                    "INSERT INTO ci_failures (repo_full_name, pr_number, workflow, classification, signature, repair_cycle) VALUES (?, ?, ?, ?, ?, 1)",
                    (repo, pr, workflow, classification, signature)
                )
                await db.commit()
                return {"action": "REPAIR", "signature": signature, "cycle": 1, "classification": classification}
