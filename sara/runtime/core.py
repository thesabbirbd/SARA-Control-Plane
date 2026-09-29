from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AgentRuntime(ABC):
    """
    Unified Runtime Abstraction for agents
    """
    def __init__(self, provider_name: str, session_id: str):
        self.provider_name = provider_name
        self.session_id = session_id
        self.state = "CREATED"
        
    @abstractmethod
    async def initialize(self) -> None:
        pass
        
    @abstractmethod
    async def run(self, task_instruction: str, context: Dict[str, Any]) -> str:
        pass
        
    @abstractmethod
    async def pause(self) -> bool:
        pass
        
    @abstractmethod
    async def resume(self) -> bool:
        pass
        
    @abstractmethod
    async def cancel(self) -> bool:
        pass

    def transition_state(self, new_state: str):
        # Basic state machine validation
        valid_states = ["CREATED", "INITIALIZING", "READY", "RUNNING", "WAITING", "PAUSED", "VERIFYING", "COMPLETED", "FAILED", "CANCELLED", "TERMINATED"]
        if new_state in valid_states:
            self.state = new_state
        else:
            raise ValueError(f"Invalid state transition: {new_state}")

class AntigravityRuntime(AgentRuntime):
    """
    Provider-specific implementation for Antigravity.
    """
    def __init__(self, session_id: str):
        super().__init__("antigravity", session_id)
        
    async def initialize(self) -> None:
        self.transition_state("INITIALIZING")
        # Logic to setup workspace and permissions
        self.transition_state("READY")
        
    async def run(self, task_instruction: str, context: Dict[str, Any]) -> str:
        self.transition_state("RUNNING")
        # In a real impl, we fork 'agy' process here
        return "Task started."
        
    async def pause(self) -> bool:
        # AGY doesn't explicitly support pausing without canceling
        # So we store a checkpoint and safely resume later.
        self.transition_state("PAUSED")
        return True
        
    async def resume(self) -> bool:
        self.transition_state("RUNNING")
        return True
        
    async def cancel(self) -> bool:
        self.transition_state("CANCELLED")
        return True
