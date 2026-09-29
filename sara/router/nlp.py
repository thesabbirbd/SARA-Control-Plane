import json
import aiohttp
from sara.config.settings import settings
from sara.core.projects import list_projects
from sara.security.redaction import redact

async def parse_intent_with_ollama(user_text: str, current_project: str = None) -> dict:
    if not settings.ollama_enabled:
        raise Exception("Ollama is disabled in configuration.")
        
    allowed = ", ".join(list_projects()) or "none yet"
    prompt = (
        "You are an intelligent NLP command router for a Telegram bot managing a DevOps automation system. "
        "Analyze the user's input and output ONLY a valid JSON object. Do not add markdown blocks or conversational text.\n"
        "ROUTING RULES:\n"
        "1. If they want to run code/tests/tasks, output: "
        '{"action": "run_antigravity", "project": "<project_name>", "instruction": "<the instruction>"} '
        f"   (Allowed projects: {allowed}. If they don't mention a project but imply coding, use '{current_project}' if available, else ask them to specify.)\n"
        "2. If they ask for system status, updates on tasks, or queue status ('what is running'), output: {\"action\": \"list_tasks\"} or {\"action\": \"system_status\"}\n"
        "3. If they ask for the status of a specific task (e.g. 'status for task 5'), output: {\"action\": \"task_status\", \"task_id\": <id>}\n"
        "4. If they want to cancel a task, output: {\"action\": \"cancel_task\", \"task_id\": <id>}\n"
        "5. If they want to retry a task or 'retry the last failed task', output: {\"action\": \"retry_task\", \"task_id\": <id or null for last failed>}\n"
        "6. If they want to check project status ('what is the status of test01'), output: {\"action\": \"project_status\", \"project\": \"<project>\"}\n"
        "7. If they just say hi, swear, ask how you are, or say something conversational, output: {\"action\": \"chat\", \"message\": \"<a witty, short, in-character response as an AI>\"}\n"
        "8. Otherwise, output {\"action\": \"unknown\"}\n"
        f"\nUser Input: '{redact(user_text)}'"
    )

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                response_text = data.get("response", "").strip()
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return {"action": "unknown"}
            else:
                raise Exception(f"Ollama API returned status {resp.status}")
