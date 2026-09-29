import httpx
import os
from typing import Dict, Any, List

class GitHubProvider:
    """Core GitHub connection, auth, and API provider."""
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}" if self.token else ""
        }
        self.base_url = "https://api.github.com"
        
    async def get_identity(self) -> Dict[str, Any]:
        if not self.token:
            return {"status": "Not Configured", "user": None}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/user", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                return {"status": "Connected", "user": data.get("login")}
            return {"status": "Error", "user": None}

    async def list_repositories(self) -> List[Dict[str, Any]]:
        # Mocked for testing without real credentials
        if not self.token:
            return [{"full_name": "test-org/repo-1", "visibility": "private", "default_branch": "main", "archived": False}]
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/user/repos", headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            return []
