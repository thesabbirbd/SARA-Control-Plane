with open("app/main.py", "r") as f:
    content = f.read()

worker_status_handler = """
async def worker_status_command(update, context):
    if not authorized(update): return
    import subprocess
    try:
        out = subprocess.check_output(['pgrep', '-af', 'app/main.py'], text=True)
        lines = [l for l in out.strip().split('\\n') if 'python' in l and 'app/main.py' in l]
        count = len(lines)
    except subprocess.SubprocessError:
        count = 0
        
    status = "HEALTHY" if count == 1 else "⚠️ Duplicate worker detected." if count > 1 else "🔴 OFFLINE"
    
    msg = f"⚙️ <b>WORKER STATUS</b>\\n\\nWorker instances detected: {count}\\nExpected: 1\\nStatus: {status}"
    await update.message.reply_html(msg)

"""

if "async def worker_status_command" not in content:
    content = content.replace("async def status_command", worker_status_handler + "\nasync def status_command")
    
    # Ensure add_handler for worker is present
    if "CommandHandler(\"worker\"" not in content:
        content = content.replace('bot_app.add_handler(CommandHandler("health", health))', 'bot_app.add_handler(CommandHandler("health", health))\n    bot_app.add_handler(CommandHandler("worker", worker_status_command))')

with open("app/main.py", "w") as f:
    f.write(content)
