import re

with open("app/main.py", "r") as f:
    content = f.read()

start_idx = content.find("async def handle_natural_language")
end_idx = content.find("async def scheduled_db_insert", start_idx)

new_func = """async def handle_natural_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    user_text = update.message.text
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
    elif user_text == "⏰ Schedule":
        await update.message.reply_html("Use <code>/schedule HH:MM &lt;project&gt; &lt;task&gt;</code> for now.")
        return
    elif user_text == "🚀 Run Task":
        await update.message.reply_html("Select a project from <b>📁 Projects</b> or just type what you want me to do!")
        return

    status_msg = await update.message.reply_markdown("🧠 *Thinking...*")
    
    intent = deterministic_router(user_text)
    
    if not intent:
        try:
            intent = await parse_intent_with_ollama(user_text)
        except Exception as e:
            print(f"Ollama parsing failed: {e}")
            intent = {"action": "unknown"}
            
    if not intent or intent.get("action") == "unknown":
        await status_msg.edit_text("👋 Hello! I am ready. Give me a coding task, or use the menu below.", parse_mode="Markdown")
        return
        
    action = intent.get("action")
    
    if action == "about":
        await status_msg.edit_text("🟢 **SABBiR Control Plane**\\nLocal automation controller\\nTelegram → Queue → Antigravity", parse_mode="Markdown")
        return
    elif action == "help":
        await status_msg.delete()
        await help_command(update, context)
        return
    elif action == "system_status":
        await status_msg.delete()
        await status_command(update, context)
        return
    elif action == "chat":
        msg = intent.get("message", "Hello!")
        await status_msg.edit_text(msg)
        return
    elif action == "list_tasks":
        await status_msg.delete()
        await tasks_command(update, context)
        return
    elif action == "task_status":
        task_id = intent.get("task_id")
        if task_id:
            await status_msg.delete()
            context.args = [str(task_id)]
            await task_status_command(update, context)
        else:
            await status_msg.edit_text("❌ Missing task ID.")
        return
    elif action == "project_status":
        project = intent.get("project")
        if project:
            await status_msg.delete()
            context.args = [project]
            await project_status_command(update, context)
        else:
            await status_msg.edit_text("❌ Missing project name.")
        return
    elif action == "cancel_task":
        task_id = intent.get("task_id")
        if not task_id:
            await status_msg.edit_text("❌ Could not determine task ID to cancel.")
            return
        await status_msg.delete()
        context.args = [str(task_id)]
        await cancel_command(update, context)
        return
    elif action == "retry_task":
        task_id = intent.get("task_id")
        if not task_id:
            await status_msg.edit_text("❌ Could not determine task ID to retry.")
            return
        await status_msg.delete()
        context.args = [str(task_id)]
        await retry_command(update, context)
        return
    elif action == "run_antigravity":
        project = intent.get("project", "")
        instruction = intent.get("instruction", "")
        
        user_id = update.effective_user.id
        
        # Fallback to session context active project
        if not project:
            active_proj = await get_active_project(user_id)
            if active_proj:
                project = active_proj
                instruction = f"(Continuing in {project}) {instruction}"
        
        # Fallback to default project
        if not project:
            default_proj = os.getenv("DEFAULT_PROJECT")
            if default_proj and default_proj in get_projects():
                project = default_proj
                instruction = f"(Using default project: {project}) {instruction}"
            else:
                await status_msg.edit_text("⚠️ Which project should I use? Please specify (e.g. 'on portfolio').")
                return
                
        if not instruction:
            await status_msg.edit_text("⚠️ Could not determine instruction.")
            return
            
        await queue_task(update, project, instruction)
        await status_msg.edit_text(
            f"🚀 <b>Task Queued</b>\\n\\n📁 Project: <code>{project}</code>\\n📝 Instruction: {instruction}\\n\\n<i>Agent will start shortly.</i>",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text("👋 Hello! I am ready. Give me a coding task or use the menu below.", parse_mode="Markdown")

"""

content = content[:start_idx] + new_func + content[end_idx:]

with open("app/main.py", "w") as f:
    f.write(content)

print("Patched.")
