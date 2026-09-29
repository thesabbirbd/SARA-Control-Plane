import os
from pathlib import Path
from typing import Optional
from sara.config.settings import settings

def normalize_path(path_str: str) -> Path:
    """Canonicalize a filesystem path, protecting against traversal."""
    # Expand ~ and resolve absolute path (handles ../ and symlinks)
    return Path(path_str).expanduser().resolve()

def is_path_allowed(path: Path) -> bool:
    """Check if the resolved path is within any allowed workspace root."""
    try:
        resolved = path.resolve(strict=False)
        for root in settings.workspace_roots:
            if root in resolved.parents or root == resolved:
                return True
        return False
    except Exception:
        return False

def get_project_dir(project_name: str) -> Optional[Path]:
    """Find a project by name across all workspace roots."""
    if not project_name: return None
    
    # Simple traversal protection just in case
    if ".." in project_name or "/" in project_name:
        return None
        
    for root in settings.workspace_roots:
        candidate = root / project_name
        if candidate.is_dir():
            return candidate
            
    return None
