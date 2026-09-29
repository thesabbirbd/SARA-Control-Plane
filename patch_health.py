import re

with open("app/main.py", "r") as f:
    content = f.read()

new_health = """async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime_seconds = int(time.time() - BOOT_TIME)
    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"
    
    disk_warning = " ⚠️" if disk >= 85 else ""
    
    ollama_status = "🔴 OFFLINE"
    if settings.ollama_enabled:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=3.0)
                if res.status_code == 200:
                    ollama_status = "🟢 ONLINE"
        except Exception:
            pass
    else:
        ollama_status = "⚪ DISABLED"
            
    msg = (
        "⚙️ <b>SYSTEM</b>\\n\\n"
        f"<b>CPU:</b>\\n{cpu}%\\n\\n"
        f"<b>RAM:</b>\\n{ram}%\\n\\n"
        f"<b>Disk:</b>\\n{disk}%{disk_warning}\\n\\n"
        f"<b>Uptime:</b>\\n{uptime_str}\\n\\n"
        "<b>Services:</b>\\n"
        "Telegram  🟢\\n"
        f"Ollama     {ollama_status}\\n"
        "Antigravity 🟢\\n\\n"
        "<b>Environment:</b>\\n"
        "Ubuntu"
    )
    await update.message.reply_html(msg)"""

content = re.sub(r"async def health\(update: Update, context: ContextTypes\.DEFAULT_TYPE\):.*?await update\.message\.reply_text\(msg\)", new_health, content, flags=re.DOTALL)

with open("app/main.py", "w") as f:
    f.write(content)
