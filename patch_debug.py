import re

with open("app/main.py", "r") as f:
    content = f.read()

debug_handler = """
async def debug_task_command(update, context):
    if not authorized(update): return
    args = context.args
    if not args:
        await update.message.reply_html("Usage: <code>/debug task &lt;id&gt;</code>")
        return
    if args[0] == "task" and len(args) > 1:
        task_id = args[1]
    else:
        task_id = args[0]
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as c:
            row = await c.fetchone()
            
    if not row:
        await update.message.reply_html("Task not found.")
        return
        
    tel = row['telemetry']
    import json
    try:
        t = json.loads(tel) if tel else {}
    except:
        t = {}
        
    msg = f"🔍 <b>DEBUG TASK #{task_id}</b>\\n\\n"
    msg += f"<b>ROUTING</b>\\nIntent: {row.get('action', 'run_antigravity')}\\n"
    msg += f"Router: {t.get('router', 'unknown')}\\n"
    msg += f"Routing time: {t.get('routing_ms', 0):.1f}ms\\n\\n"
    
    msg += f"<b>QUEUE</b>\\nWait time: {t.get('queue_wait_ms', 0):.1f}ms\\n\\n"
    
    msg += f"<b>PROCESS</b>\\nPID: {row['pid']}\\n"
    alive = "Yes" if row['pid'] and row['status'] == 'RUNNING' else "No"
    msg += f"Alive: {alive}\\n\\n"
    
    msg += f"<b>AGENT</b>\\nProvider: Antigravity\\n"
    msg += f"Runtime: {t.get('agent_runtime_ms', 0):.1f}ms\\n\\n"
    
    msg += f"<b>RESULT</b>\\n{row['status']}\\n\\n"
    
    msg += f"<b>TELEGRAM</b>\\nDelivery: {t.get('telegram_send_ms', 0):.1f}ms\\n"
    
    await update.message.reply_html(msg)

"""

content = content.replace("async def start_command", debug_handler + "\nasync def start_command")
content = content.replace('bot_app.add_handler(CommandHandler("history", history_command))', 'bot_app.add_handler(CommandHandler("history", history_command))\n    bot_app.add_handler(CommandHandler("debug", debug_task_command))')

with open("app/main.py", "w") as f:
    f.write(content)
