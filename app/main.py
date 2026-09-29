import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sara.config.settings import settings
from sara.security.risk import classify_command, RiskLevel
from sara.security.redaction import redact
scheduler = None
import asyncio
import json
import re
import signal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiosqlite
import random
import psutil
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv()

ALLOWED_USER_ID = int(os.environ.get("TELEGRAM_ALLOWED_USER_ID", 0))
AGY_BIN = os.getenv("ANTIGRAVITY_BIN", "agy")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

# Determine base paths dynamically
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)

DB_PATH = os.environ.get("SARA_DB_PATH", os.path.join(PROJECT_ROOT, "queue.db"))
# Default BASE_DIR to the parent of the project root if not specified
BASE_DIR = Path(os.environ.get("SARA_PROJECTS_DIR", os.path.dirname(PROJECT_ROOT))).expanduser().resolve()
BASE_DIR.mkdir(parents=True, exist_ok=True)

bot_app = None
scheduler = AsyncIOScheduler()

async def get_active_project(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT active_project FROM sessions WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_active_project(user_id: int, project: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO sessions (user_id, active_project) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET active_project = excluded.active_project, updated_at = CURRENT_TIMESTAMP
        ''', (user_id, project))
        await db.commit()



async def get_notify_preference(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            async with db.execute("SELECT notify_enabled FROM sessions WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return bool(row[0]) if row and row[0] is not None else True
        except Exception:
            return True

async def toggle_notify_preference(user_id: int) -> bool:
    current = await get_notify_preference(user_id)
    new_val = 0 if current else 1
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("INSERT INTO sessions (user_id, notify_enabled) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET notify_enabled = excluded.notify_enabled, updated_at = CURRENT_TIMESTAMP", (user_id, new_val))
            await db.commit()
        except Exception:
            pass
    return bool(new_val)

async def startup_recovery():

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status IN ('RUNNING', 'STARTING')") as cursor:
            tasks = await cursor.fetchall()
            
        for t in tasks:
            if not is_process_alive(t['pid']):
                await transition_task(db, t['id'], "INTERRUPTED")
        await db.commit()

async def stale_task_recovery():
    while True:
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM tasks WHERE status = 'RUNNING'") as cursor:
                    tasks = await cursor.fetchall()
                for t in tasks:
                    if not is_process_alive(t['pid']):
                        await transition_task(db, t['id'], "INTERRUPTED")
                await db.commit()
        except Exception as e:
            print("Stale recovery error:", e)
        await asyncio.sleep(10)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                instruction TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                pid INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                active_project TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try:
            await db.execute("ALTER TABLE sessions ADD COLUMN notify_enabled INTEGER DEFAULT 1")
        except Exception:
            pass
        await db.commit()


def is_process_alive(pid: int) -> bool:
    if not pid: return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def authorized(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id == ALLOWED_USER_ID

def get_projects():
    if not BASE_DIR.exists():
        return []
    return [d.name for d in BASE_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]

def get_secure_project_dir(project_name: str) -> Path | None:
    try:
        proj_dir = (BASE_DIR / project_name).resolve()
        if proj_dir.is_relative_to(BASE_DIR) and proj_dir != BASE_DIR:
            return proj_dir
    except Exception:
        pass
    return None

def get_git_info(project_name: str):
    proj_dir = get_secure_project_dir(project_name)
    if not proj_dir or not (proj_dir / ".git").exists():
        return None
    try:
        import subprocess
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=str(proj_dir), stderr=subprocess.DEVNULL).decode().strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(proj_dir), stderr=subprocess.DEVNULL).decode().strip()
        commit = subprocess.check_output(["git", "log", "-1", "--format=%h - %s"], cwd=str(proj_dir), stderr=subprocess.DEVNULL).decode().strip()
        return {
            "branch": branch,
            "clean": len(status) == 0,
            "commit": commit
        }
    except Exception:
        return None

def get_dashboard_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🚀 Run Task"), KeyboardButton("📋 My Tasks")],
            [KeyboardButton("📊 Status"), KeyboardButton("📁 Projects")],
            [KeyboardButton("⏰ Schedule"), KeyboardButton("⚙️ System")],
            [KeyboardButton("🔔 Notifications")]
        ],
        resize_keyboard=True
    )

def resolve_project_alias(text: str) -> str:
    projects = get_projects()
    text = text.lower()
    for p in projects:
        if p.lower() in text:
            return p
    # Hardcoded aliases
    if "portfolio" in text: return "portfolio"
    if "study" in text: return "studyos"
    if "control" in text: return "sabbiR-control-plane"
    return ""

def deterministic_router(user_text: str):
    text = user_text.lower().strip()
    if text in ["help", "/help"]: return {"action": "help"}
    if text in ["start", "/start"]: return {"action": "start"}
    if text in ["status", "/status", "system status"]: return {"action": "system_status"}
    if text in ["tasks", "/tasks", "queue", "show tasks"]: return {"action": "list_tasks"}
    if text in ["history", "/history"]: return {"action": "history"}
    if text in ["projects", "/projects"]: return {"action": "list_projects"}
    if text in ["health", "/health"]: return {"action": "system_status"}
    if text in ["about", "/about"]: return {"action": "about"}
    m = re.match(r'^(?:task )?status(?:\s+for)?\s+(?:task\s+)?(\d+)$', text)
    if m: return {"action": "task_status", "task_id": int(m.group(1))}
    m = re.match(r'^(?:cancel|stop)(?:\s+task)?\s+(\d+)$', text)
    if m: return {"action": "cancel_task", "task_id": int(m.group(1))}
    m = re.match(r'^(?:retry|run again)(?:\s+task)?\s+(\d+)$', text)
    if m: return {"action": "retry_task", "task_id": int(m.group(1))}
    m = re.match(r'^(?:project )?status(?:\s+for)?\s+([a-z0-9_-]+)$', text)
    if m:
        p = resolve_project_alias(m.group(1))
        if p: return {"action": "project_status", "project": p}
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    text = (
        "🟢 <b>SABBiR Control Plane</b>\n\n"
        "Your remote engineering console is ONLINE.\n\n"
        "💻 Ubuntu\n"
        "🤖 Antigravity: Ready\n"
        "🧠 Ollama: Ready\n\n"
        "Choose an action below or simply type what you want me to do."
    )
    await update.message.reply_html(text, reply_markup=get_dashboard_keyboard())

async def new_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/new &lt;project_name&gt;</code>")
        return
    project_name = context.args[0]
    proj_dir = get_secure_project_dir(project_name)
    if not proj_dir:
        await update.message.reply_html(f"❌ Invalid project name: <b>{project_name}</b>")
        return
    if proj_dir.exists():
        await update.message.reply_html(f"⚠️ Project <b>{project_name}</b> already exists!")
        return
    proj_dir.mkdir(parents=True, exist_ok=True)
    await update.message.reply_html(f"✅ Successfully created new project: <b>{project_name}</b>")

async def list_projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    projects = get_projects()
    if not projects:
        await update.message.reply_html("No projects found.")
        return
        
    user_id = update.effective_user.id
    active_proj = await get_active_project(user_id)
    
    text = "📁 <b>PROJECT HUB</b>\n\nSelect a project below to set it as active, or type a command for it.\n\n"
    for p in projects:
        icon = "⭐" if p == active_proj else "📁"
        text += f"{icon} <code>{p}</code>\n"
        
    keyboard = []
    for p in projects:
        keyboard.append([InlineKeyboardButton(f"⭐ Set Active: {p}", callback_data=f"set_active_{p}")])
        
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    text = (
        "🛠️ <b>Control Plane Commands:</b>\n\n"
        "<code>/start</code> - Wake up the bot\n"
        "<code>/help</code> - Show this menu\n"
        "<code>/ag &lt;project&gt; &lt;task&gt;</code> - Manually run a task\n"
        "<code>/status</code> - Check overall system status\n"
        "<code>/tasks</code> - List pending and running tasks\n"
        "<code>/history</code> - View recent task history\n"
        "<code>/cancel &lt;id&gt;</code> - Cancel a specific task\n"
        "<code>/retry &lt;id&gt;</code> - Retry a failed task\n"
        "<code>/schedule HH:MM &lt;project&gt; &lt;task&gt;</code> - Schedule a task\n"
        "<code>/health</code> - System health\n"
        "<code>/funfact</code> - Random tech fact\n"
        "<code>/new &lt;name&gt;</code> - Create new project\n"
        "<code>/projects</code> - List projects"
    )
    await update.message.reply_html(text)


VALID_TRANSITIONS = {
    'PENDING': ['STARTING', 'CANCELLED'],
    'STARTING': ['RUNNING', 'FAILED', 'CANCELLED', 'INTERRUPTED'],
    'RUNNING': ['SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED'],
    'SUCCESS': [],
    'FAILED': ['PENDING'],
    'TIMEOUT': ['PENDING'],
    'CANCELLED': ['PENDING'],
    'INTERRUPTED': ['PENDING']
}

async def transition_task(db, task_id: int, new_status: str, pid: int = None, exit_code: int = None, error_msg: str = None):
    async with db.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)) as c:
        row = await c.fetchone()
        if not row: raise ValueError(f"Task {task_id} not found")
        current_status = row[0]
        
    if new_status not in VALID_TRANSITIONS.get(current_status, []) and new_status != 'PENDING':
        raise ValueError(f"Illegal transition: {current_status} -> {new_status}")
            
    updates = ["status = ?"]
    params = [new_status]
    
    if pid is not None:
        updates.append("pid = ?")
        params.append(pid)
    if exit_code is not None:
        updates.append("exit_code = ?")
        params.append(exit_code)
    if error_msg is not None:
        updates.append("error_message = ?")
        params.append(error_msg)
    if new_status == 'STARTING':
        updates.append("started_at = CURRENT_TIMESTAMP")
    if new_status in ['SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED']:
        updates.append("finished_at = CURRENT_TIMESTAMP")
        
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    params.append(task_id)
    
    await db.execute(query, tuple(params))
    await db.commit()

async def queue_task(update: Update, project: str, instruction: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO tasks (project_name, instruction, status) VALUES (?, ?, 'PENDING')",
            (project, instruction)
        )
        task_id = cursor.lastrowid
        await db.commit()
    
    await update.message.reply_html(
        f"✅ <b>Task added to queue (ID: {task_id})</b>\n"
        f"📁 Project: <code>{project}</code>\n"
        f"📝 Instruction: <i>{instruction}</i>\n"
        f"The background worker will process it shortly."
    )

async def ag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if len(context.args) < 2:
        await update.message.reply_html("Usage: <code>/ag &lt;project&gt; &lt;instruction&gt;</code>")
        return
    project = context.args[0]
    instruction = " ".join(context.args[1:])
    await queue_task(update, project, instruction)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"

async def parse_intent_with_gemini(user_text: str, current_project: str = None) -> dict:
    allowed = ", ".join(get_projects()) or "none yet"
    prompt = (
        "You are an intelligent NLP command router for a Telegram bot managing a DevOps automation system. "
        "Analyze the user's input and output ONLY a valid JSON object. Do not add markdown blocks or conversational text.\n"
        "ROUTING RULES:\n"
        "1. If they want to run code/tests/tasks, output: "
        "{\"action\": \"run_antigravity\", \"project\": \"<project_name>\", \"instruction\": \"<the instruction>\"} "
        f"   (Allowed projects: {allowed}. If they don't mention a project but imply coding, use '{current_project}' if available, else ask them to specify.)\n"
        "2. If they ask for system status, updates on tasks, or queue status ('what is running'), output: {\"action\": \"list_tasks\"} or {\"action\": \"system_status\"}\n"
        "3. If they ask for the status of a specific task (e.g. 'status for task 5'), output: {\"action\": \"task_status\", \"task_id\": <id>}\n"
        "4. If they want to cancel a task, output: {\"action\": \"cancel_task\", \"task_id\": <id>}\n"
        "5. If they want to retry a task or 'retry the last failed task', output: {\"action\": \"retry_task\", \"task_id\": <id or null for last failed>}\n"
        "6. If they want to check project status ('what is the status of test01'), output: {\"action\": \"project_status\", \"project\": \"<project>\"}\n"
        "7. If they just say hi, swear, ask how you are, or say something conversational, output: {\"action\": \"chat\", \"message\": \"<a witty, short, in-character response as an AI>\"}\n"
        "8. Otherwise, output {\"action\": \"unknown\"}\n"
        f"\nUser Input: '{user_text}'"
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GEMINI_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15.0
            )
            
            if response.status_code != 200:
                return {"action": "api_error", "message": f"HTTP {response.status_code}: {response.text}"}

            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return {"action": "api_error", "message": "No candidates returned from Gemini."}

            print(f"RAW GEMINI: {raw_text}")

            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                return json.loads(raw_text)

    except Exception as e:
        return {"action": "api_error", "message": f"{type(e).__name__}: {str(e)}"}

async def handle_natural_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    user_text = update.message.text
    if not user_text: return
    if user_text.startswith('/'): return
    
    # Deterministic Button Intercepts
    if user_text == "📊 Status":
        await status_command(update, context)
        return
    elif user_text == "📋 My Tasks":
        await tasks_command(update, context)
        return
    elif user_text == "📁 Projects":
        await list_projects_command(update, context)
        return
    elif user_text == "⚙️ System":
        await health(update, context)
        return
    elif user_text == "🔔 Notifications":
        new_val = await toggle_notify_preference(update.effective_user.id)
        state = "ON 🟢" if new_val else "OFF 🔴"
        await update.message.reply_html(f"🔔 Antigravity Task Notifications are now <b>{state}</b>.")
        return
    elif user_text == "⏰ Schedule":
        await update.message.reply_html("Use <code>/schedule HH:MM &lt;project&gt; &lt;task&gt;</code> for now.")
        return
    elif user_text == "🚀 Run Task":
        user_id = update.effective_user.id
        active_proj = await get_active_project(user_id)
        if active_proj:
            await update.message.reply_html(f"⭐ Active project is <b>{active_proj}</b>.\nJust type your task instructions and I'll send it to Antigravity!")
        else:
            await update.message.reply_html("Select a project from <b>📁 Projects</b> first, then type what you want me to do!")
        return

    status_msg = await update.message.reply_markdown("🧠 *Thinking...*")
    
    intent = deterministic_router(user_text)
    
    if not intent:
        try:
            user_id = update.effective_user.id
            active_proj = await get_active_project(user_id)
            intent = await parse_intent_with_gemini(user_text, active_proj)
        except Exception as e:
            print(f"Gemini parsing failed: {e}")
            intent = {"action": "api_error"}
            
    action = intent.get("action") if intent else "unknown"
    
    # Fallback directly to Antigravity if the intent is unknown or Gemini fails
    if action in ("unknown", "api_error") or not intent:
        user_id = update.effective_user.id
        active_proj = await get_active_project(user_id)
        if active_proj:
            await status_msg.edit_text(f"🤖 **Direct Fallback**\nSending to Antigravity on `[{active_proj}]`...", parse_mode="Markdown")
            await queue_task(update, active_proj, user_text)
        else:
            await status_msg.edit_text("❌ I didn't understand the command, and Gemini API is unreachable/failing. Please set an active project first from 📁 Projects to send direct tasks.")
        return
    elif action == "about":
        await status_msg.edit_text("🟢 **SABBiR Control Plane**\nLocal automation controller\nTelegram → Queue → Antigravity", parse_mode="Markdown")
        return
    elif action == "help":
        await status_msg.delete()
        await help_command(update, context)
        return
    elif action == "system_status":
        await status_msg.delete()
        await status_command(update, context)
        return
    elif action == "chat":
        msg = intent.get("message", "Hello!")
        await status_msg.edit_text(msg)
        return
    elif action == "list_tasks":
        await status_msg.delete()
        await tasks_command(update, context)
        return
    elif action == "task_status":
        task_id = intent.get("task_id")
        if task_id:
            await status_msg.delete()
            context.args = [str(task_id)]
            await task_status_command(update, context)
        else:
            await status_msg.edit_text("❌ Missing task ID.")
        return
    elif action == "project_status":
        project = intent.get("project")
        if project:
            await status_msg.delete()
            context.args = [project]
            await project_status_command(update, context)
        else:
            await status_msg.edit_text("❌ Missing project name.")
        return
    elif action == "cancel_task":
        task_id = intent.get("task_id")
        if not task_id:
            await status_msg.edit_text("❌ Could not determine task ID to cancel.")
            return
        await status_msg.delete()
        context.args = [str(task_id)]
        await cancel_command(update, context)
        return
    elif action == "retry_task":
        task_id = intent.get("task_id")
        if not task_id:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT id FROM tasks WHERE status IN ('FAILED', 'INTERRUPTED') ORDER BY id DESC LIMIT 1") as c:
                    row = await c.fetchone()
                    if row: task_id = row['id']
        if not task_id:
            await status_msg.edit_text("❌ No failed tasks found to retry.")
            return
        await status_msg.delete()
        context.args = [str(task_id)]
        await retry_command(update, context)
        return
    elif action == "run_antigravity":
        project = intent.get("project", "")
        instruction = intent.get("instruction", "")
        
        user_id = update.effective_user.id
        
        # Fallback to session context active project
        if not project:
            active_proj = await get_active_project(user_id)
            if active_proj:
                project = active_proj
                instruction = f"(Continuing in {project}) {instruction}"
        
        if not project:
            await status_msg.edit_text("❌ Please specify a project name, or select one from the /projects menu first.")
            return
                
        if not instruction:
            await status_msg.edit_text("⚠️ Could not determine instruction.")
            return
            
        await queue_task(update, project, instruction)
        await status_msg.edit_text(
            f"🚀 <b>Task Queued</b>\n\n📁 Project: <code>{project}</code>\n📝 Instruction: {instruction}\n\n<i>Agent will start shortly.</i>",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text("👋 Hello! I am ready. Give me a coding task or use the menu below.", parse_mode="Markdown")

async def scheduled_db_insert(project, instruction):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tasks (project_name, instruction, status) VALUES (?, ?, 'PENDING')",
            (project, instruction)
        )
        await db.commit()

async def schedule_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if len(context.args) < 3:
        await update.message.reply_html("Usage: <code>/schedule HH:MM &lt;project&gt; &lt;instruction&gt;</code>")
        return
        
    time_str = context.args[0]
    project = context.args[1]
    instruction = " ".join(context.args[2:])
    
    try:
        hour, minute = map(int, time_str.split(':'))
        now = datetime.now()
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_time <= now:
            run_time += timedelta(days=1)
            
        scheduler.add_job(scheduled_db_insert, 'date', run_date=run_time, args=[project, instruction])
        await update.message.reply_html(f"⏰ Task scheduled for <b>{run_time.strftime('%Y-%m-%d %H:%M')}</b>.\nIt will automatically enter the queue at that time.")
    except Exception as e:
        await update.message.reply_html(f"❌ Invalid time format. Use HH:MM (24-hour). Error: {e}")

import time

BOOT_TIME = psutil.boot_time()

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime_seconds = int(time.time() - BOOT_TIME)
    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"
    
    gemini_status = "🔴 OFFLINE"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("https://generativelanguage.googleapis.com/v1beta/models?key=" + GEMINI_API_KEY, timeout=3.0)
            if res.status_code == 200:
                gemini_status = "🟢 ONLINE"
    except Exception:
        pass
        
    text = (
        "⚙️ <b>SYSTEM CENTER</b>\n\n"
        f"<b>CPU:</b>      {cpu}%\n"
        f"<b>RAM:</b>      {ram}%\n"
        f"<b>Disk:</b>     {disk}%\n"
        f"<b>Uptime:</b>   {uptime_str}\n\n"
        "🌐 <b>SERVICES</b>\n"
        f"Gemini:      {gemini_status}\n"
        "Antigravity: 🟢 (CLI Available)\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_system")]
    ]
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
            await update.callback_query.answer("Refreshed!")
        except Exception:
            await update.callback_query.answer("Already up to date.")
    else:
        await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def funfact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    facts = [
        "The first computer bug was an actual real-life moth found in a Harvard Mark II computer in 1947.",
        "Python is named after the British comedy troupe Monty Python, not the snake.",
        "The first programmer in the world was Ada Lovelace, who wrote an algorithm for Charles Babbage's early mechanical general-purpose computer.",
        "There are over 700 programming languages, but just 10 of them dominate 80% of software development.",
        "Google's first storage rack for its servers was built using Lego bricks."
    ]
    await update.message.reply_html(f"💡 <b>Fun Fact:</b>\n{random.choice(facts)}")

async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status IN ('PENDING', 'RUNNING') ORDER BY created_at ASC LIMIT 10") as cursor:
            tasks = await cursor.fetchall()
            
    if not tasks:
        await update.message.reply_html("✅ <b>Queue is empty.</b>")
        return
        
    text = "📋 <b>ACTIVE QUEUE</b>\n\n"
    for t in tasks:
        if t['status'] == 'RUNNING':
            text += f"▶️ <b>#{t['id']} {t['project_name']}</b>\n   <i>Running...</i>\n\n"
        else:
            text += f"⏳ <b>#{t['id']} {t['project_name']}</b>\n   <i>Pending...</i>\n\n"
            
    text += "<i>(Showing up to 10 tasks)</i>\n"
    
    keyboard = []
    if any(t['status'] == 'PENDING' for t in tasks):
        keyboard.append([InlineKeyboardButton("🧹 Clear Pending", callback_data="clear_queue")])
    
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None)

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status NOT IN ('PENDING', 'RUNNING') ORDER BY id DESC LIMIT 5") as cursor:
            tasks = await cursor.fetchall()
            
    if not tasks:
        await update.message.reply_html("📚 <b>History is empty.</b>")
        return
        
    text = "📚 <b>TASK HISTORY</b>\n\n"
    for t in tasks:
        icon = "✅" if t['status'] == 'SUCCESS' else "❌" if t['status'] == 'FAILED' else "⏹"
        text += f"{icon} <b>#{t['id']} {t['project_name']}</b> ({t['status']})\n   <i>{t['instruction'][:50]}...</i>\n\n"
        
    await update.message.reply_html(text)

async def task_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/taskstatus &lt;id&gt;</code>")
        return
    task_id = context.args[0]
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            task = await cursor.fetchone()
    if not task:
        await update.message.reply_html(f"❌ Task <b>#{task_id}</b> not found.")
        return
    
    icon = "⏳" if task['status'] == 'PENDING' else "▶️" if task['status'] == 'RUNNING' else "✅" if task['status'] == 'SUCCESS' else "❌"
    text = f"{icon} <b>Task #{task['id']}</b>\nProject: <code>{task['project_name']}</code>\nStatus: <b>{task['status']}</b>\nInstruction: <i>{task['instruction']}</i>"
    await update.message.reply_html(text)

async def project_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/projectstatus &lt;project&gt;</code>")
        return
    project = context.args[0]
    
    git_info = get_git_info(project)
    if git_info is None:
        await update.message.reply_html(f"❌ Project <b>{project}</b> not found or has no Git repository.")
        return
        
    status_icon = "🟢 Clean" if git_info['clean'] else "🟡 Uncommitted Changes"
    text = (
        f"📁 <b>Project: {project}</b>\n\n"
        f"🌿 <b>Git Status</b>\n"
        f"Branch: <code>{git_info['branch']}</code>\n"
        f"Tree: {status_icon}\n"
        f"Last: <code>{git_info['commit']}</code>\n\n"
    )
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE project_name = ? AND status IN ('PENDING', 'RUNNING')", (project,)) as cursor:
            active_tasks = (await cursor.fetchone())[0]
            
    text += f"Active Tasks: <b>{active_tasks}</b>"
    await update.message.reply_html(text)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/cancel &lt;id&gt;</code>")
        return
    task_id = context.args[0]
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            task = await cursor.fetchone()
            
    if not task:
        await update.message.reply_html(f"❌ Task <b>#{task_id}</b> not found.")
        return
        
    if task['status'] not in ['PENDING', 'STARTING', 'RUNNING']:
        await update.message.reply_html(f"⚠️ Task #{task_id} is already <b>{task['status']}</b>.")
        return
        
    async with aiosqlite.connect(DB_PATH) as db:
        if task['pid'] and is_process_alive(task['pid']):
            try:
                # Kill process group
                os.killpg(os.getpgid(task['pid']), signal.SIGTERM)
                await asyncio.sleep(1)
                if is_process_alive(task['pid']):
                    os.killpg(os.getpgid(task['pid']), signal.SIGKILL)
            except Exception as e:
                pass
        
        await transition_task(db, task_id, "CANCELLED")
        await db.commit()
        
    await update.message.reply_html(f"🛑 Task <b>#{task_id}</b> cancelled safely.")

async def retry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/retry &lt;id&gt;</code>")
        return
    task_id = context.args[0]
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            task = await cursor.fetchone()
            
    if not task:
        await update.message.reply_html(f"❌ Task <b>#{task_id}</b> not found.")
        return
        
    if task['status'] in ['PENDING', 'RUNNING', 'STARTING']:
        await update.message.reply_html(f"⚠️ Task #{task_id} is currently <b>{task['status']}</b>. Cannot retry.")
        return
        
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tasks (project_name, instruction, status, parent_task_id) VALUES (?, ?, 'PENDING', ?)",
            (task['project_name'], task['instruction'], task['id'])
        )
        cursor2 = await db.execute("SELECT last_insert_rowid()"); new_id = (await cursor2.fetchone())[0]
        await db.commit()
        
    await update.message.reply_html(f"🔁 <b>Task Queued for Retry</b>\nOld Task: #{task_id}\nNew Task: #{new_id}\n\n<i>Worker will pick this up shortly.</i>")

async def background_worker():
    print("Background worker started.")
    
    # Ensure logs directory
    LOGS_DIR = Path(__file__).parent.parent / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    while True:
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                # Safety check: don't start new if one is RUNNING
                async with db.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('STARTING', 'RUNNING')") as cursor:
                    active = (await cursor.fetchone())[0]
                    
                if active == 0:
                    async with db.execute("SELECT value FROM system_config WHERE key = 'queue_paused'") as cursor:
                        row = await cursor.fetchone()
                        is_paused = row and row[0] == 'true'
                    task = None
                    if not is_paused:
                        async with db.execute("SELECT * FROM tasks WHERE status = 'PENDING' AND (next_attempt IS NULL OR next_attempt <= CURRENT_TIMESTAMP) AND (depends_on IS NULL OR depends_on IN (SELECT id FROM tasks WHERE status = 'SUCCESS')) ORDER BY CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'normal' THEN 3 WHEN 'low' THEN 4 ELSE 3 END, created_at ASC LIMIT 1") as cursor:
                            task = await cursor.fetchone()
                    
                    if task:
                        task_id = task['id']
                        project = task['project_name']
                        instruction = task['instruction']
                        
                        await transition_task(db, task_id, "STARTING")
                        await db.commit()
                        
                        start_time = datetime.now()
                        msg_text = (
                            f"▶️ <b>Task #{task_id} STARTED</b>\n\n"
                            f"📁 <code>{project}</code>\n"
                            f"🤖 Antigravity\n\n"
                            f"Started: {start_time.strftime('%H:%M:%S')}"
                        )
                        if task['parent_task_id']:
                            msg_text += f"\n🔁 <i>Retry of Task #{task['parent_task_id']}</i>"
                            
                        await bot_app.bot.send_message(
                            chat_id=ALLOWED_USER_ID,
                            text=msg_text,
                            parse_mode="HTML"
                        )
                        
                        project_dir = get_secure_project_dir(project)
                        log_file_path = LOGS_DIR / f"task_{task_id}.log"
                        
                        await db.execute("UPDATE tasks SET log_path = ? WHERE id = ?", (str(log_file_path), task_id))
                        await db.commit()
                        
                        if not project_dir:
                            await db.execute("UPDATE tasks SET status = 'FAILED', error_message = ? WHERE id = ?", (f"Invalid project name: {project}", task_id))
                            await db.commit()
                            continue

                        if not project_dir.exists():
                            await transition_task(db, task_id, "FAILED", error_msg=f"Project not found: {project_dir}")
                            await db.commit()
                            continue
                            
                        # Helper to stream output
                        async def stream_output(stream, log_file, prefix=""):
                            async for line in stream:
                                decoded = line.decode('utf-8', errors='replace')
                                log_file.write(decoded)
                                log_file.flush()
                                os.fsync(log_file.fileno())
                                print(f"{prefix}{decoded}", end="", flush=True)

                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"\n\n--- STARTING TASK #{task_id} AT {datetime.now()} ---\n")
                            log_file.write(f"Project: {project}\nInstruction: {instruction}\n")
                            log_file.flush()
                            
                            process = await asyncio.create_subprocess_exec(
                                AGY_BIN, "-p", instruction, "--output-format", "json",
                                "--print-timeout", "30m", "--dangerously-skip-permissions",
                                cwd=str(project_dir),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                preexec_fn=os.setsid  # Put in its own process group
                            )
                            
                            await transition_task(db, task_id, "RUNNING", pid=process.pid)
                            await db.commit()
                            
                            # Update PID in message
                            await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"🔧 Task #{task_id} PID: <code>{process.pid}</code>", parse_mode="HTML")
                            
                            # Wait for it, but allow timeouts and cancellations
                            try:
                                # 30 min timeout
                                await asyncio.wait_for(
                                    asyncio.gather(
                                        stream_output(process.stdout, log_file),
                                        stream_output(process.stderr, log_file, prefix="ERR: "),
                                        process.wait()
                                    ),
                                    timeout=1800
                                )
                                exit_code = process.returncode
                                
                                async with db.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)) as c:
                                    curr = await c.fetchone()
                                    
                                if curr and curr['status'] == 'CANCELLED':
                                    pass # Handled by cancel_command
                                else:
                                    status = 'SUCCESS' if exit_code == 0 else 'FAILED'
                                    if status == 'FAILED':
                                        async with db.execute("SELECT retry_count FROM tasks WHERE id = ?", (task_id,)) as rc:
                                            r_row = await rc.fetchone()
                                            current_retries = r_row[0] if r_row else 0
                                        if current_retries < 3:
                                            delay_mins = [1, 5, 15][current_retries]
                                            await db.execute(f"UPDATE tasks SET retry_count = retry_count + 1, next_attempt = datetime('now', '+{delay_mins} minutes') WHERE id = ?", (task_id,))
                                            await transition_task(db, task_id, 'PENDING')
                                            await db.commit()
                                        else:
                                            await transition_task(db, task_id, status, exit_code=exit_code)
                                            await db.commit()
                                    else:
                                        await transition_task(db, task_id, status, exit_code=exit_code)
                                        await db.commit()
                                    
                                    icon = "✅" if status == 'SUCCESS' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"
                                    
                                    fin_text = (
                                        f"{icon} <b>Task #{task_id} COMPLETED</b>\n\n"
                                        f"Duration: {dur_str}\n"
                                        f"Exit code: {exit_code}\n"
                                        f"Log: <code>{log_file_path.name}</code>"
                                    )
                                    keyboard = [[InlineKeyboardButton("🔁 Retry", callback_data=f"retry_{task_id}")]] if status != 'SUCCESS' else []
                                    notify = await get_notify_preference(ALLOWED_USER_ID)
                                    if notify or status != 'SUCCESS':
                                        await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=fin_text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None, parse_mode="HTML")
                                    
                            except asyncio.TimeoutError:
                                # Timeout triggered
                                try:
                                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                                    await asyncio.sleep(1)
                                    if is_process_alive(process.pid):
                                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                                except Exception:
                                    pass
                                    
                                await transition_task(db, task_id, "TIMEOUT")
                                await db.commit()
                                
                                await bot_app.bot.send_message(
                                    chat_id=ALLOWED_USER_ID, 
                                    text=f"⏱ <b>Task #{task_id} TIMEOUT</b>\n\n30-minute execution limit reached.\nProcess terminated safely.", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Retry", callback_data=f"retry_{task_id}")]]),
                                    parse_mode="HTML"
                                )
                                
        except Exception as e:
            print(f"Worker error: {e}")
            
        await asyncio.sleep(3)



async def post_init(app: Application):
    await init_db()
    await startup_recovery()
    asyncio.create_task(stale_task_recovery())
        # Start Scheduler
    global scheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()
    print("APScheduler started.", flush=True)
    asyncio.create_task(background_worker())

def main():
    if not settings.telegram_bot_token:
        print("ERROR: TELEGRAM_settings.telegram_bot_token not set!")
        return
        
    global bot_app
    bot_app = Application.builder().token(settings.telegram_bot_token).post_init(post_init).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("new", new_project))
    bot_app.add_handler(CommandHandler("projects", list_projects_command))
    bot_app.add_handler(CommandHandler("status", status_command))
    bot_app.add_handler(CommandHandler("schedule", schedule_task_command))
    bot_app.add_handler(CommandHandler("tasks", tasks_command))
    bot_app.add_handler(CommandHandler("history", history_command))
    bot_app.add_handler(CommandHandler("cancel", cancel_command))
    bot_app.add_handler(CommandHandler("retry", retry_command))
    bot_app.add_handler(CommandHandler("health", health))
    bot_app.add_handler(CommandHandler("funfact", funfact))
    bot_app.add_handler(CommandHandler("ag", ag_command))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language))

    print("SABBiR Control Plane (Phase 2 - Queue) started.")
    bot_app.run_polling(allowed_updates=Update.ALL_TYPES)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await health(update, context)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    print(f"Callback received: {data}", flush=True)
    
    if data.startswith("retry_"):
        task_id = data.split("_")[1]
        context.args = [task_id]
        await retry_command(update, context)
        
    elif data.startswith("cancel_"):
        task_id = data.split("_")[1]
        context.args = [task_id]
        await cancel_command(update, context)
        
    elif data.startswith("set_active_"):
        project = data.replace("set_active_", "")
        try:
            await set_active_project(update.effective_user.id, project)
            await query.edit_message_text(f"⭐ Active project set to: {project}", parse_mode="HTML")
            print(f"Successfully set active project to {project}", flush=True)
        except Exception as e:
            print(f"Error setting active project: {e}", flush=True)

if __name__ == "__main__":
    main()
