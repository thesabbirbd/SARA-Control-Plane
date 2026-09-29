import subprocess
from typing import List, Optional, Dict
from pathlib import Path
from sara.config.settings import settings
from sara.security.workspace import is_path_allowed, get_project_dir

def list_projects() -> List[str]:
    """Discover Git projects under allowed workspace roots."""
    projects = []
    for root in settings.workspace_roots:
        if not root.is_dir():
            continue
        # Scan 1 level deep for .git folders
        for child in root.iterdir():
            if child.is_dir() and (child / '.git').is_dir():
                projects.append(child.name)
    return sorted(list(set(projects)))

def get_git_info(project_name: str) -> Optional[Dict]:
    proj_dir = get_project_dir(project_name)
    if not proj_dir or not (proj_dir / '.git').exists():
        return None
        
    try:
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current'], 
            cwd=str(proj_dir), stderr=subprocess.DEVNULL, text=True
        ).strip()
        
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'], 
            cwd=str(proj_dir), stderr=subprocess.DEVNULL, text=True
        )
        
        commit = subprocess.check_output(
            ['git', 'log', '-1', '--format=%h'], 
            cwd=str(proj_dir), stderr=subprocess.DEVNULL, text=True
        ).strip()
        
        return {
            'branch': branch or 'HEAD',
            'clean': len(status.strip()) == 0,
            'commit': commit
        }
    except subprocess.SubprocessError:
        return {'branch': 'unknown', 'clean': False, 'commit': 'unknown'}
