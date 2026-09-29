from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator

class AgentProvider(ABC):
    
    @abstractmethod
    async def execute(self, project_path: str, instruction: str, task_id: int) -> int:
        """Executes a task and returns the exit code."""
        pass
        
    @abstractmethod
    async def capabilities(self) -> Dict[str, bool]:
        """Returns a dict of capabilities like 'supports_streaming', 'supports_background'."""
        pass
