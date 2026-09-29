import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import deterministic_router, resolve_project_alias, get_projects

def mock_get_projects():
    return ["test01", "portfolio", "sabbiR-control-plane"]

import main
main.get_projects = mock_get_projects

def test_router():
    assert deterministic_router("who are you") == {"action": "about"}
    assert deterministic_router("help") == {"action": "help"}
    assert deterministic_router("system status") == {"action": "system_status"}
    assert deterministic_router("what is running") == {"action": "list_tasks"}
    assert deterministic_router("status for task id 5") == {"action": "task_status", "task_id": 5}
    assert deterministic_router("status for test01") == {"action": "project_status", "project": "test01"}
    assert deterministic_router("cancel task 5") == {"action": "cancel_task", "task_id": 5}
    assert deterministic_router("retry task 5") == {"action": "retry_task", "task_id": 5}
    
    # Ambiguous / Ollama expected
    assert deterministic_router("fix the navbar") is None
    assert deterministic_router("use Antigravity on my portfolio") is None
    
    print("All routing tests passed!")

if __name__ == "__main__":
    test_router()
