import json
import aiohttp
from sara.config.settings import settings
from sara.core.projects import list_projects
from sara.security.redaction import redact

async def parse_intent_with_ollama(user_text: str, current_project: str = None) -> dict:
    if not settings.ollama_enabled:
        raise Exception("Ollama is disabled in configuration.")
        
    allowed = ", ".join(list_projects()) or "none yet"
    prompt = f"""You are the SARA Control Plane NLP semantic router.
You must categorize the user's message into exactly one of these intents:
GREETING, CONTROL, INFORMATION, PROJECT_INTELLIGENCE, ARTIFACT, SCHEDULING, DEVELOPMENT, UNKNOWN.

Output ONLY a valid JSON object. No markdown.

RULES:
1. GREETING: basic hello, thanks, etc. -> {{"action": "greeting"}}
2. CONTROL: cancel tasks, stop, retry -> {{"action": "cancel_task", "task_id": <id>}} or {{"action": "retry_task", "task_id": <id>}}
3. INFORMATION: status of system, queue -> {{"action": "system_status"}} or {{"action": "list_tasks"}}
4. PROJECT_INTELLIGENCE: what changed, latest progress, project status -> {{"action": "project_update"}}
5. ARTIFACT: send log, show output -> {{"action": "send_log", "task_id": <id>}} or {{"action": "task_result", "task_id": <id>}}
6. SCHEDULING: run at 11pm -> {{"action": "schedule"}}
7. DEVELOPMENT: explicitly asking to write code, fix bugs, create files, run scripts, test things. -> {{"action": "run_antigravity", "project": "{current_project or 'null'}", "instruction": "..."}}
8. UNKNOWN: ambiguous -> {{"action": "clarify", "message": "Can you clarify?"}}

User Input: '{redact(user_text)}'
"""

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=5) as resp:
            if resp.status == 200:
                data = await resp.json()
                response_text = data.get("response", "").strip()
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return {"action": "clarify", "message": "Can you clarify?"}
            else:
                raise Exception(f"Ollama API returned status {resp.status}")
