import re

with open("app/main.py", "r") as f:
    content = f.read()

worker_status_handler = """
async def worker_status_command(update, context):
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

content = content.replace("async def start_command", worker_status_handler + "\nasync def start_command")
content = content.replace("bot_app.add_handler(CommandHandler(\"health\", health))", "bot_app.add_handler(CommandHandler(\"health\", health))\n    bot_app.add_handler(CommandHandler(\"worker\", worker_status_command))")

with open("app/main.py", "w") as f:
    f.write(content)
