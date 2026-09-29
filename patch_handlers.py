import re

with open("app/main.py", "r") as f:
    content = f.read()

# Add send_log_command, send_latest_log_command, task_result_command, project_update_command
new_commands = """
async def send_log_command(update, context, task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT project_name, log_path FROM tasks WHERE id = ?", (task_id,)) as c:
            row = await c.fetchone()
    if not row or not row['log_path']:
        await update.message.reply_html(f"⚠️ <b>Log unavailable</b>\n\nTask #{task_id} exists,\nbut its log file could not be found.")
        return
    log_file = Path(row['log_path'])
    if not log_file.exists():
        await update.message.reply_html(f"⚠️ <b>Log unavailable</b>\n\nTask #{task_id} log file is missing from disk.")
        return
    
    caption = f"📎 <b>TASK #{task_id} LOG</b>\n\nProject:\n{row['project_name']}\n\nFile:\n{log_file.name}\n\nSize:\n{log_file.stat().st_size / 1024:.1f} KB"
    await update.message.reply_document(document=open(log_file, 'rb'), caption=caption, parse_mode='HTML')

async def send_latest_log_command(update, context):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id FROM tasks WHERE log_path IS NOT NULL ORDER BY id DESC LIMIT 1") as c:
            row = await c.fetchone()
    if not row:
        await update.message.reply_html("⚠️ No tasks with logs found.")
        return
    await send_log_command(update, context, row['id'])

async def task_result_command(update, context, task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as c:
            row = await c.fetchone()
            
    if not row:
        await update.message.reply_html(f"❌ Task #{task_id} not found.")
        return
        
    status = row['status']
    icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "▶️" if status == "RUNNING" else "⏳"
    
    # Extract actual result if it exists (from log if short enough, or from a new 'result' column if we added it)
    log_content = "No output available."
    if row['log_path']:
        p = Path(row['log_path'])
        if p.exists():
            try:
                log_content = p.read_text(errors='replace')
                if len(log_content) > 1000:
                    log_content = log_content[-1000:] + "\n...(truncated)"
            except:
                pass
                
    result_text = f"{icon} <b>TASK #{task_id} {status}</b>\n\n<b>Result:</b>\n<pre>{log_content}</pre>"
    await update.message.reply_html(result_text)

async def project_update_command(update, context, project_name):
    # Deterministic Project update based on Git + Tasks
    try:
        from sara.core.projects import get_git_info
        git_info = get_git_info(project_name)
    except:
        git_info = None
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, status FROM tasks WHERE project_name = ? ORDER BY id DESC LIMIT 5", (project_name,)) as c:
            tasks = await c.fetchall()
            
    task_str = ""
    for t in tasks:
        icon = "✅" if t['status'] == "SUCCESS" else "❌" if t['status'] == "FAILED" else "▶️"
        task_str += f"{icon} #{t['id']}\n"
        
    git_str = "Not available"
    if git_info:
        git_str = f"Branch: {git_info['branch']}\nWorking tree: {'Clean' if git_info['clean'] else 'Modified'}\nLatest commit: {git_info['commit']}"
        
    msg = f"📌 <b>PROJECT UPDATE</b>\n\n📁 <b>{project_name}</b>\n\n<b>Recent tasks:</b>\n{task_str}\n<b>Git:</b>\n{git_str}"
    await update.message.reply_html(msg)

"""

# Insert new commands before handle_natural_language
content = content.replace("async def handle_natural_language", new_commands + "\nasync def handle_natural_language")

# Now inject the new handlers into handle_natural_language
handler_block = """    elif action == "project_status":"""
new_handlers = """    elif action == "send_log":
        task_id = intent.get("task_id")
        await status_msg.delete()
        if task_id:
            await send_log_command(update, context, task_id)
        return
    elif action == "send_latest_log":
        await status_msg.delete()
        await send_latest_log_command(update, context)
        return
    elif action == "task_result":
        task_id = intent.get("task_id")
        await status_msg.delete()
        if task_id:
            await task_result_command(update, context, task_id)
        return
    elif action == "project_update":
        await status_msg.delete()
        user_id = update.effective_user.id
        active_proj = await get_active_project(user_id)
        if not active_proj:
            await update.message.reply_html("❌ No active project set. Select one from <b>📁 Projects</b> first.")
        else:
            await project_update_command(update, context, active_proj)
        return
    elif action == "project_status":"""

content = content.replace(handler_block, new_handlers)

# Fix Gemini/Ollama intent logic
old_intent_block = """    if not intent:
        try:
            user_id = update.effective_user.id
            active_proj = await get_active_project(user_id)
            intent = await parse_intent_with_gemini(user_text, active_proj)
        except Exception as e:
            print(f"Gemini parsing failed: {e}")
            intent = {"action": "api_error"}"""

new_intent_block = """    if not intent:
        try:
            from sara.config.settings import settings
            user_id = update.effective_user.id
            active_proj = await get_active_project(user_id)
            if settings.ollama_enabled:
                from sara.router.nlp import parse_intent_with_ollama
                intent = await parse_intent_with_ollama(user_text, active_proj)
            else:
                intent = None
        except Exception as e:
            print(f"NLP parsing failed: {e}")
            intent = {"action": "api_error"}"""

content = content.replace(old_intent_block, new_intent_block)

# Fix the direct fallback text
content = content.replace("Gemini API is unreachable/failing", "NLP parsing is unreachable/failing or disabled")

with open("app/main.py", "w") as f:
    f.write(content)
