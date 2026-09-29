with open("app/main.py", "r") as f:
    content = f.read()

import re

# Find the tasks_command
start = content.find("async def tasks_command")
end = content.find("async def history_command")

new_tasks_command = """async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 15") as cursor:
            tasks = await cursor.fetchall()
            
    if not tasks:
        await update.message.reply_html("✅ <b>Queue is empty.</b>")
        return
        
    text = "📋 <b>TASK CENTER</b>\\n\\n"
    
    running = [t for t in tasks if t['status'] == 'RUNNING']
    pending = [t for t in tasks if t['status'] == 'PENDING']
    failed = [t for t in tasks if t['status'] == 'FAILED']
    completed = [t for t in tasks if t['status'] == 'SUCCESS']
    
    if running:
        text += "▶️ <b>RUNNING</b>\\n"
        for t in running: text += f"#{t['id']} {t['project_name']} - <i>{t['instruction'][:30]}...</i>\\n"
        text += "\\n"
    if pending:
        text += "⏳ <b>PENDING</b>\\n"
        for t in pending: text += f"#{t['id']} {t['project_name']} - <i>{t['instruction'][:30]}...</i>\\n"
        text += "\\n"
    if failed:
        text += "❌ <b>FAILED</b>\\n"
        for t in failed[:3]: text += f"#{t['id']} {t['project_name']} - <i>{t['instruction'][:30]}...</i>\\n"
        text += "\\n"
    if completed:
        text += "✅ <b>COMPLETED</b>\\n"
        for t in completed[:3]: text += f"#{t['id']} {t['project_name']} - <i>{t['instruction'][:30]}...</i>\\n"
        text += "\\n"
    
    keyboard = []
    if pending:
        keyboard.append([InlineKeyboardButton("🧹 Clear Pending", callback_data="clear_queue")])
    
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None)

"""

if start != -1 and end != -1:
    content = content[:start] + new_tasks_command + content[end:]
    with open("app/main.py", "w") as f:
        f.write(content)
