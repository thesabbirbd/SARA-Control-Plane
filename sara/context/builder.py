import os
import subprocess
from typing import Dict, Any

class ProjectContextBuilder:
    def __init__(self, workspace_root: str, project_name: str):
        self.workspace_root = workspace_root
        self.project_name = project_name
        self.project_path = os.path.join(workspace_root, project_name)

    def _get_git_summary(self) -> str:
        if not os.path.exists(os.path.join(self.project_path, ".git")):
            return "No Git repository found."
        try:
            branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=self.project_path, text=True).strip()
            status = subprocess.check_output(["git", "status", "-s"], cwd=self.project_path, text=True).strip()
            return f"Branch: {branch}\nStatus:\n{status if status else 'Clean'}"
        except Exception:
            return "Failed to retrieve Git summary."

    def _get_project_rules(self) -> str:
        rules_files = ["SARA.md", "AGENTS.md", "PROJECT_RULES.md"]
        for rf in rules_files:
            fp = os.path.join(self.project_path, rf)
            if os.path.exists(fp):
                with open(fp, "r") as f:
                    return f"Loaded rules from {rf}:\n" + f.read()[:2000] # Compress context
        return "No explicit project rules found."

    def build_context(self) -> Dict[str, Any]:
        """
        Compresses and bounds project context.
        """
        if not os.path.exists(self.project_path):
            return {"error": "Project not found"}
        
        return {
            "project": self.project_name,
            "git": self._get_git_summary(),
            "rules": self._get_project_rules(),
            "path": self.project_path
        }
