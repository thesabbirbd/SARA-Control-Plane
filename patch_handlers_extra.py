import re

with open("app/main.py", "r") as f:
    content = f.read()

extra_handlers = """
async def greeting_command(update, context):
    user_id = update.effective_user.id
    active_proj = await get_active_project(user_id) or "None"
    await update.message.reply_html(f"👋 <b>Hi!</b>\\n\\nSARA is online and ready.\\n\\nCurrent project:\\n<code>{active_proj}</code>\\n\\nHow can I help?")

async def cancel_all_command(update, context):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tasks SET status = 'CANCELLED' WHERE status IN ('PENDING')")
        
        # Kill running
        async with db.execute("SELECT id, pid FROM tasks WHERE status = 'RUNNING'") as cursor:
            running_tasks = await cursor.fetchall()
            
        for t in running_tasks:
            try:
                import os, signal
                if t['pid']: os.killpg(os.getpgid(t['pid']), signal.SIGTERM)
            except: pass
            
        await db.execute("UPDATE tasks SET status = 'CANCELLED' WHERE status = 'RUNNING'")
        await db.commit()
        
    await update.message.reply_html("🛑 <b>CANCEL ALL</b>\\n\\nQueue:\\n⏸ stopped")

async def ollama_status_command(update, context):
    import time, httpx
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post("http://127.0.0.1:11434/api/generate", json={"model": settings.ollama_model, "prompt": "Reply exactly OLLAMA_OK", "stream": False})
            latency = (time.time() - start) * 1000
            if resp.status_code == 200:
                status = "🟢 ONLINE"
                msg = f"🧠 <b>OLLAMA</b>\\n\\nStatus:\\n{status}\\n\\nModel:\\n{settings.ollama_model}\\n\\nLatency:\\n{latency:.0f}ms"
            else:
                msg = f"🧠 <b>OLLAMA</b>\\n\\nStatus:\\n⚠️ ERROR ({resp.status_code})"
    except Exception as e:
        msg = f"🧠 <b>OLLAMA</b>\\n\\nStatus:\\n🔴 OFFLINE\\nError: {str(e)}"
        
    await update.message.reply_html(msg)

"""

# Insert before start_command
content = content.replace("async def start_command", extra_handlers + "\nasync def start_command")

with open("app/main.py", "w") as f:
    f.write(content)
