import re

with open("app/main.py", "r") as f:
    content = f.read()

start = content.find("async def handle_natural_language(")
end = content.find("async def start_command")

new_handle = """async def handle_natural_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    intent = deterministic_router(user_text)
    user_id = update.effective_user.id
    active_proj = await get_active_project(user_id)
    
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
            context.args = [intent.get("task_id")]
            await cancel_command(update, context)
            return
        elif action == "retry_task":
            await status_msg.delete()
            context.args = [intent.get("task_id")]
            await retry_command(update, context)
            return
            
    if not intent:
        try:
            from sara.config.settings import settings
            if settings.ollama_enabled:
                from sara.router.nlp import parse_intent_with_ollama
                intent = await parse_intent_with_ollama(user_text, active_proj)
            else:
                intent = None
        except Exception as e:
            print(f"NLP parsing failed: {e}")
            intent = {"action": "api_error"}
            
    action = intent.get("action") if intent else "unknown"
    
    if action in ("unknown", "api_error", "run_antigravity") or not intent:
        if active_proj:
            await status_msg.edit_text(f"🤖 **Direct Fallback**\\nSending to Antigravity on `[{active_proj}]`...", parse_mode="Markdown")
            await queue_task(update, active_proj, user_text)
        else:
            await status_msg.edit_text("⚠️ Please select an active project from <b>📁 Projects</b> first.", parse_mode="HTML")

"""

if start != -1 and end != -1:
    content = content[:start] + new_handle + "\n" + content[end:]
    with open("app/main.py", "w") as f:
        f.write(content)
