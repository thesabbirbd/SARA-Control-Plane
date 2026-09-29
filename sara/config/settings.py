from dotenv import load_dotenv
load_dotenv()
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from pydantic import SecretStr

@dataclass
class Settings:
    sara_env: str = os.getenv("SARA_ENV", "development")
    telegram_bot_token: SecretStr = field(default_factory=lambda: SecretStr(os.getenv("TELEGRAM_BOT_TOKEN", "")))
    telegram_allowed_user_ids: List[int] = field(default_factory=list)
    default_project: Optional[str] = os.getenv("DEFAULT_PROJECT")
    default_agent: str = os.getenv("DEFAULT_AGENT", "antigravity")
    
    ollama_enabled: bool = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    workspace_roots: List[Path] = field(default_factory=list)
    
    queue_concurrency: int = int(os.getenv("QUEUE_CONCURRENCY", "1"))
    agy_timeout_seconds: int = int(os.getenv("AGY_TIMEOUT_SECONDS", "1800"))
    
    notification_level: str = os.getenv("NOTIFICATION_LEVEL", "important")
    confirm_dangerous: bool = os.getenv("CONFIRM_DANGEROUS", "true").lower() == "true"
    auto_retry_interrupted: bool = os.getenv("AUTO_RETRY_INTERRUPTED", "false").lower() == "true"
    
    db_path: Path = Path("queue.db").resolve()
    
    def __post_init__(self):
        # Parse allowed users
        raw_users = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
        if raw_users:
            self.telegram_allowed_user_ids = [int(x.strip()) for x in raw_users.split(",") if x.strip().isdigit()]
            
        # Parse workspace roots
        raw_roots = os.getenv("WORKSPACE_ROOTS", "")
        if raw_roots:
            self.workspace_roots = [Path(x.strip()).expanduser().resolve() for x in raw_roots.split(",") if x.strip()]
        else:
            self.workspace_roots = [Path.home() / "projects"] # Safe fallback

settings = Settings()
