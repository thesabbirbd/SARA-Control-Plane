from typing import Dict, List
from sara.database.core import get_db

class ReleaseEngine:
    """Release Engineering and Changelog generation."""
    
    @staticmethod
    def generate_changelog(commits: List[Dict[str, str]]) -> str:
        features, fixes, other = [], [], []
        for c in commits:
            msg = c.get('message', '').lower()
            if msg.startswith('feat') or 'add' in msg:
                features.append(c['message'])
            elif msg.startswith('fix') or 'bug' in msg:
                fixes.append(c['message'])
            else:
                other.append(c['message'])
                
        changelog = "## Features\\n" + "\\n".join(f"- {f}" for f in features)
        changelog += "\\n\\n## Fixes\\n" + "\\n".join(f"- {f}" for f in fixes)
        return changelog

    @staticmethod
    def check_readiness(checks: List[Dict]) -> bool:
        # Require all checks to pass for a release
        for check in checks:
            if check['status'] != 'PASS':
                return False
        return True

    @staticmethod
    async def create_release_record(repo: str, version: str, strategy: str):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO project_releases (repo_full_name, version, strategy, status) VALUES (?, ?, ?, 'DRAFT')",
                (repo, version, strategy)
            )
            await db.commit()
