import re
import json
import httpx
from app.core.config import GEMINI_API_KEY
from app.utils.helpers import get_projects

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

def deterministic_router(user_text: str):
    text = user_text.strip().lower()
    if text in ["/help", "help", "what can you do"]:
        return {"action": "help"}
    if text in ["/start", "start"]:
        return {"action": "start"}
    if text in ["/status", "status", "system status"]:
        return {"action": "system_status"}
    if text in ["/tasks", "tasks", "queue"]:
        return {"action": "list_tasks"}
    if text in ["/projects", "projects"]:
        return {"action": "list_projects"}
    if text in ["/history", "history"]:
        return {"action": "history"}
    if text in ["/health", "health"]:
        return {"action": "system_status"}
    if text in ["/about", "about"]:
        return {"action": "about"}
    
    m_status = re.match(r'^(?:task )?status(?:\s+for)?\s+(?:task\s+)?(\d+)$', text)
    if m_status:
        return {"action": "task_status", "task_id": int(m_status.group(1))}
        
    m_cancel = re.match(r'^cancel\s+(?:task\s+)?(\d+)$', text)
    if m_cancel:
        return {"action": "cancel_task", "task_id": int(m_cancel.group(1))}
        
    m_retry = re.match(r'^retry\s+(?:task\s+)?(\d+)$', text)
    if m_retry:
        return {"action": "retry_task", "task_id": int(m_retry.group(1))}

    return None

async def parse_intent_with_gemini(user_text: str, current_project: str = None) -> dict:
    allowed = ", ".join(get_projects()) or "none yet"
    prompt = (
        "You are an intelligent NLP command router for a Telegram bot managing a DevOps automation system. "
        "The user will give you a command. Your job is to parse their intent into a strict JSON object.\n\n"
        f"Available Projects: [{allowed}]\n"
        f"Currently Active Project: {current_project if current_project else 'None'}\n\n"
        "Possible output formats (Choose ONE and output ONLY valid JSON, nothing else):\n"
        "1. If they want to run a task/command/script on a project:\n"
        '   {"action": "run_antigravity", "project": "<project_name>", "instruction": "<what to do>"}\n'
        "   (If they don't mention a project, use the Currently Active Project. If there is no active project, set project to null).\n"
        "2. If they just say hi, thanks, or ask a general conversational question:\n"
        '   {"action": "chat", "message": "<a witty, very short reply acknowledging them>"}\n'
        "3. If you absolutely cannot understand:\n"
        '   {"action": "unknown"}\n\n'
        f"User Command: {user_text}\n"
    )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GEMINI_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return json.loads(raw_text.strip())
    except httpx.ReadTimeout:
        return {"action": "api_error", "message": "Gemini API Timeout"}
    except Exception as e:
        return {"action": "api_error", "message": str(e)}
