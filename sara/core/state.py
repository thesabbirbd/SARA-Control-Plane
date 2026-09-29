from sara.database.core import get_db
from sara.core.events import EventBus

class WorkflowState:
    RECEIVED = "RECEIVED"
    PLANNING = "PLANNING"
    PLANNED = "PLANNED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    READY_FOR_DEPLOY = "READY_FOR_DEPLOY"
    DEPLOYING = "DEPLOYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"

class StateMachine:
    @staticmethod
    async def transition(workflow_id: str, new_state: str, reason: str = ""):
        # Assumes objectives table represents the workflow for now
        async with get_db() as db:
            await db.execute(
                "UPDATE objectives SET status = ? WHERE id = ?",
                (new_state, workflow_id)
            )
            await db.commit()
            
        await EventBus.publish(f"workflow.state_changed", workflow_id, {"to": new_state, "reason": reason})
