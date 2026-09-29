with open("app/main.py", "r") as f:
    content = f.read()

import re

new_router = r"""def deterministic_router(user_text: str):
    text = user_text.lower().strip()
    if text in ["help", "/help"]: return {"action": "help"}
    if text in ["start", "/start"]: return {"action": "start"}
    if text in ["status", "/status", "system status"]: return {"action": "system_status"}
    if text in ["tasks", "/tasks", "queue", "show tasks", "what is running right now"]: return {"action": "list_tasks"}
    if text in ["history", "/history"]: return {"action": "history"}
    if text in ["projects", "/projects"]: return {"action": "list_projects"}
    if text in ["health", "/health", "system health"]: return {"action": "system_status"}
    if text in ["about", "/about"]: return {"action": "about"}
    
    if text in ["what's the update", "whats the update", "whats the udpate", "last features for this project", "what changed recently?", "what has antigravity done recently?"]: 
        return {"action": "project_update"}
        
    m = re.match(r'^(?:task )?status(?:\s+for)?\s+(?:task\s+)?(\d+)$', text)
    if not m: m = re.match(r'^status for task id (\d+)$', text)
    if m: return {"action": "task_status", "task_id": int(m.group(1))}
    
    m = re.match(r'^(?:cancel|stop)(?:\s+task)?\s+(\d+)$', text)
    if m: return {"action": "cancel_task", "task_id": int(m.group(1))}
    
    m = re.match(r'^(?:retry|run again)(?:\s+task)?\s+(\d+)$', text)
    if m: return {"action": "retry_task", "task_id": int(m.group(1))}
    
    m = re.match(r'^(?:project )?status(?:\s+for)?\s+([a-z0-9_-]+)$', text)
    if m:
        p = resolve_project_alias(m.group(1))
        if p: return {"action": "project_status", "project": p}
        
    # Artifacts (Logs)
    m = re.match(r'^(?:send|give|show) (?:me )?(?:the )?(?:latest )?task (\d+) log(?: file)?(?: in chat)?$', text)
    if not m: m = re.match(r'^(?:send|give) (?:me )?log(?: for)? task (\d+)$', text)
    if not m: m = re.match(r'^send task (\d+) log$', text)
    if m: return {"action": "send_log", "task_id": int(m.group(1))}
    
    # Latest log
    if text in ["send latest log", "send me the latest task log"]:
        return {"action": "send_latest_log"}
        
    # Task Output
    m = re.match(r'^(?:show|send) (?:me )?(?:the )?output (?:from|for) task (\d+)$', text)
    if not m: m = re.match(r'^show task (\d+) output$', text)
    if m: return {"action": "task_result", "task_id": int(m.group(1))}
        
    return None"""

content = re.sub(r"def deterministic_router.*?return None", lambda x: new_router, content, flags=re.DOTALL)

with open("app/main.py", "w") as f:
    f.write(content)
