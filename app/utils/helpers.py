import os
import psutil
from app.core.config import BASE_DIR

def is_process_alive(pid: int) -> bool:
    if pid is None:
        return False
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False

def get_projects():
    if not BASE_DIR.exists():
        return []
    return [d.name for d in BASE_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]

def get_git_info(project_name: str):
    import subprocess
    proj_dir = BASE_DIR / project_name
    if not (proj_dir / ".git").exists():
        return ""
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=proj_dir, stderr=subprocess.DEVNULL).decode().strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=proj_dir, stderr=subprocess.DEVNULL).decode().strip()
        state = "dirty ⚠️" if status else "clean ✅"
        return f"[{branch} | {state}]"
    except Exception:
        return ""

def resolve_project_alias(text: str) -> str:
    # Optional logic if user misstypes
    text_lower = text.lower()
    projects = get_projects()
    for p in projects:
        if text_lower == p.lower():
            return p
    return None
