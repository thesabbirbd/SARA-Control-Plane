from sara.database.core import get_db
import re

class IssueTriage:
    """Issue Classification and Triage Engine."""
    
    @staticmethod
    def classify(title: str, body: str, labels: list) -> str:
        text = f"{title} {body}".lower()
        if "security" in labels or "CVE" in text.upper():
            return "SECURITY"
        if "bug" in labels or "fix" in text or "error" in text:
            return "BUG"
        if "feature" in labels or "enhancement" in labels or "add" in text:
            return "FEATURE"
        if "dependency" in labels or "dependabot" in text:
            return "DEPENDENCY"
        return "UNKNOWN"
        
    @staticmethod
    def calculate_priority(classification: str, age_days: int) -> int:
        prio = 0
        if classification == "SECURITY": prio += 100
        elif classification == "BUG": prio += 50
        
        # Age adds priority urgency
        prio += min(age_days, 30)
        return prio
        
    @staticmethod
    async def register_issue(repo: str, issue_number: int, title: str, body: str, labels: list, age_days: int = 0):
        cls = IssueTriage.classify(title, body, labels)
        prio = IssueTriage.calculate_priority(cls, age_days)
        
        async with get_db() as db:
            await db.execute(
                "INSERT OR REPLACE INTO github_issues (repo_full_name, issue_number, classification, priority, state) VALUES (?, ?, ?, ?, 'OPEN')",
                (repo, issue_number, cls, prio)
            )
            await db.commit()
