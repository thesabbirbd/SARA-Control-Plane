import re

with open("app/main.py", "r") as f:
    content = f.read()

start = content.find("async def handle_natural_language(")
end = content.find("async def start_command")

new_handle = """async def handle_natural_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    import time
    start_time = time.time()
    
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
        await (update.message or update.callback_query.message).reply_html(f"🔔 Antigravity Task Notifications are now <b>{state}</b>.")
        return
    elif user_text == "⏰ Schedule":
        await (update.message or update.callback_query.message).reply_html("Use <code>/schedule HH:MM &lt;project&gt; &lt;task&gt;</code> for now.")
        return
    elif user_text == "🚀 Run Task":
        user_id = update.effective_user.id
        active_proj = await get_active_project(user_id)
        if active_proj:
            await (update.message or update.callback_query.message).reply_html(f"⭐ Active project is <b>{active_proj}</b>.\\nJust type your task instructions and I'll send it to Antigravity!")
        else:
            await (update.message or update.callback_query.message).reply_html("Select a project from <b>📁 Projects</b> first, then type what you want me to do!")
        return

    status_msg = await (update.message or update.callback_query.message).reply_markdown("🧠 *Thinking...*")
    
    route_start = time.time()
    intent = deterministic_router(user_text)
    route_time = (time.time() - route_start) * 1000
    
    user_id = update.effective_user.id
    active_proj = await get_active_project(user_id)
    
    router_used = "deterministic"
    ollama_time = 0
    
    if not intent:
        ollama_start = time.time()
        try:
            from sara.config.settings import settings
            if settings.ollama_enabled:
                from sara.router.nlp import parse_intent_with_ollama
                intent = await parse_intent_with_ollama(user_text, active_proj)
                router_used = "ollama"
            else:
                intent = None
        except Exception as e:
            print(f"NLP parsing failed: {e}")
            intent = {"action": "clarify"}
        ollama_time = (time.time() - ollama_start) * 1000
            
    if intent:
        action = intent.get("action")
        if action == "greeting":
            await status_msg.delete()
            await greeting_command(update, context)
            return
        elif action == "cancel_all":
            await status_msg.delete()
            await cancel_all_command(update, context)
            return
        elif action == "ollama_status":
            await status_msg.delete()
            await ollama_status_command(update, context)
            return
        elif action == "list_tasks":
            await status_msg.delete()
            await tasks_command(update, context)
            return
        elif action == "system_status":
            await status_msg.delete()
            await status_command(update, context)
            return
        elif action == "project_update":
            await status_msg.delete()
            await project_update_command(update, context, active_proj)
            return
        elif action == "task_status":
            await status_msg.delete()
            await task_result_command(update, context, intent.get("task_id"))
            return
        elif action == "send_log":
            await status_msg.delete()
            await send_log_command(update, context, intent.get("task_id"))
            return
        elif action == "task_result":
            await status_msg.delete()
            await task_result_command(update, context, intent.get("task_id"))
            return
        elif action == "send_latest_log":
            await status_msg.delete()
            await send_latest_log_command(update, context)
            return
        elif action == "cancel_task":
            await status_msg.delete()
            context.args = [str(intent.get("task_id"))]
            await cancel_command(update, context)
            return
        elif action == "retry_task":
            await status_msg.delete()
            context.args = [str(intent.get("task_id"))]
            await retry_command(update, context)
            return
        elif action == "clarify":
            await status_msg.edit_text("🤖 Could you clarify? (This was not recognized as a development task).")
            return
            
    action = intent.get("action") if intent else "unknown"
    
    if action in ("run_antigravity",):
        if active_proj:
            await status_msg.edit_text(f"🤖 **Direct Fallback**\\nSending to Antigravity on `[{active_proj}]`...", parse_mode="Markdown")
            
            # Queue task with telemetry
            import json
            tel = json.dumps({"router": router_used, "routing_ms": route_time, "ollama_ms": ollama_time, "telegram_received_ms": start_time*1000})
            
            instruction = intent.get("instruction", user_text)
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "INSERT INTO tasks (project_name, instruction, chat_id, message_id, status, telemetry) VALUES (?, ?, ?, ?, ?, ?)",
                    (active_proj, instruction, update.message.chat_id, update.message.message_id, "PENDING", tel)
                )
                await db.commit()
                async with db.execute("SELECT last_insert_rowid()") as cursor:
                    task_id = (await cursor.fetchone())[0]
                    
            await status_msg.edit_text(
                f"✅ **Task added to queue** (ID: {task_id})\\n\\n"
                f"📁 Project: `{active_proj}`\\n"
                f"📝 Instruction: `{instruction}`\\n\\n"
                f"The background worker will process it shortly.",
                parse_mode="Markdown"
            )
        else:
            await status_msg.edit_text("⚠️ Please select an active project from <b>📁 Projects</b> first.", parse_mode="HTML")
    else:
        await status_msg.edit_text("🤖 I didn't understand that command. Use /help or select an option below.", parse_mode="HTML")
"""

if start != -1 and end != -1:
    content = content[:start] + new_handle + "\n" + content[end:]
    with open("app/main.py", "w") as f:
        f.write(content)
