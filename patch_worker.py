import re

with open("app/main.py", "r") as f:
    content = f.read()

# Update the end of the execution block in background_worker
old_block = """                                    fin_text = (
                                        f"{icon} <b>Task #{task_id} COMPLETED</b>\\n\\n\""""

new_block = """                                    # Attempt to parse last line as JSON for result
                                    result_str = None
                                    try:
                                        with open(log_file_path, "r") as lf:
                                            lines = lf.readlines()
                                            if lines:
                                                import json
                                                last_line = lines[-1].strip()
                                                parsed = json.loads(last_line)
                                                result_str = parsed.get("response")
                                                if result_str:
                                                    await db.execute("UPDATE tasks SET result = ? WHERE id = ?", (result_str, task_id))
                                                    await db.commit()
                                    except Exception:
                                        pass
                                        
                                    fin_text = (
                                        f"{icon} <b>TASK #{task_id} COMPLETED</b>\\n\\n"
                                        f"📁 <b>Project</b>\\n{project}\\n\\n"
                                        f"🤖 <b>Agent</b>\\nAntigravity\\n\\n"
                                        f"⏱ <b>Duration</b>\\n{dur_str}\\n\\n"
                                    )
                                    if result_str:
                                        short_res = result_str if len(result_str) < 800 else result_str[:800] + "...(truncated)"
                                        fin_text += f"📝 <b>Result</b>\\n<pre>{short_res}</pre>\\n\\n"
"""

content = content.replace(old_block, new_block)

old_buttons = """                                    if status == 'FAILED':
                                        fin_text += f"❌ Exit code: {exit_code}\\n"
                                        fin_text += f"<i>Task failed and exceeded retries.</i>"
                                    
                                    await bot_app.bot.send_message(
                                        chat_id=ALLOWED_USER_ID,
                                        text=fin_text,
                                        parse_mode="HTML"
                                    )"""

new_buttons = """                                    if status == 'FAILED':
                                        fin_text = (
                                            f"❌ <b>TASK #{task_id} FAILED</b>\\n\\n"
                                            f"Antigravity exited with code {exit_code}.\\n"
                                            f"I preserved the full execution log.\\n"
                                        )
                                    
                                    # Add inline buttons
                                    fin_keyboard = [
                                        [InlineKeyboardButton("📄 Result", callback_data=f"result_{task_id}"),
                                         InlineKeyboardButton("📎 Send Log", callback_data=f"log_{task_id}")],
                                    ]
                                    if status == 'FAILED':
                                        fin_keyboard.append([InlineKeyboardButton("🔁 Retry", callback_data=f"retry_{task_id}")])
                                        
                                    await bot_app.bot.send_message(
                                        chat_id=ALLOWED_USER_ID,
                                        text=fin_text,
                                        parse_mode="HTML",
                                        reply_markup=InlineKeyboardMarkup(fin_keyboard)
                                    )"""

content = content.replace(old_buttons, new_buttons)

with open("app/main.py", "w") as f:
    f.write(content)
