with open("app/main.py", "r") as f:
    content = f.read()

import re

start = content.find("async def status_command")
end = content.find("async def button_handler")

new_status = """async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    user_id = update.effective_user.id
    active_proj = await get_active_project(user_id) or "None"
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE status = 'RUNNING'") as c:
            running = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE status = 'PENDING'") as c:
            pending = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM tasks WHERE status = 'FAILED'") as c:
            failed = (await c.fetchone())[0]
        async with db.execute("SELECT id, status FROM tasks ORDER BY id DESC LIMIT 1") as c:
            row = await c.fetchone()
            last_task = f"#{row['id']} {row['status']}" if row else "None"
            
    msg = (
        "📊 <b>CONTROL PLANE STATUS</b>\\n\\n"
        "🟢 Online\\n\\n"
        f"<b>Current Project:</b>\\n{active_proj}\\n\\n"
        f"<b>Queue:</b>\\nRunning: {running}\\nPending: {pending}\\nFailed: {failed}\\n\\n"
        "<b>Agent:</b>\\nAntigravity READY\\n\\n"
        f"<b>Last Task:</b>\\n{last_task}"
    )
    await update.message.reply_html(msg)

"""
if start != -1 and end != -1:
    content = content[:start] + new_status + content[end:]
    with open("app/main.py", "w") as f:
        f.write(content)
