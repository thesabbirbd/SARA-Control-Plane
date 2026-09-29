import re
with open("app/main.py", "r") as f:
    content = f.read()

# Remove the first send_message block
bad_block = """                        if task['parent_task_id']:
                            msg_text += f"\\n🔁 <i>Retry of Task #{task['parent_task_id']}</i>"
                            
                        await bot_app.bot.send_message(
                            chat_id=ALLOWED_USER_ID,
                            text=msg_text,
                            parse_mode="HTML"
                        )"""

# Insert send_message after process creation
good_block = """                        if task['parent_task_id']:
                            msg_text += f"\\n🔁 <i>Retry of Task #{task['parent_task_id']}</i>"
                            
                        # msg_text saved for later"""

content = content.replace(bad_block, good_block)

bad_process = """                            await transition_task(db, task_id, "RUNNING", pid=process.pid)
                            await db.commit()"""

good_process = """                            await transition_task(db, task_id, "RUNNING", pid=process.pid)
                            await db.commit()
                            
                            try:
                                msg_text = msg_text.replace("Running...", f"PID:\\n{process.pid}\\n\\nLive activity:\\nRunning...")
                                await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=msg_text, parse_mode="HTML")
                            except: pass"""

content = content.replace(bad_process, good_process)

with open("app/main.py", "w") as f:
    f.write(content)
