import re
with open("sara/router/nlp.py", "r") as f:
    content = f.read()

content = content.replace("7. DEVELOPMENT: explicitly asking to write code", "7. CONTINUE: 'Continue', 'Go on' -> {\"action\": \"continue_task\"}\n8. DEVELOPMENT: explicitly asking to write code")
with open("sara/router/nlp.py", "w") as f:
    f.write(content)

with open("app/main.py", "r") as f:
    main = f.read()

continue_logic = """        elif action == "continue_task":
            await status_msg.delete()
            # Find the last active session for this project
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT id FROM agent_sessions WHERE project_name = ? ORDER BY last_active_at DESC LIMIT 1", (active_proj,)) as c:
                    row = await c.fetchone()
                    session_id = row['id'] if row else None
            
            if not session_id:
                await (update.message or update.callback_query.message).reply_html("No active session found to continue.")
                return
                
            async with aiosqlite.connect(DB_PATH) as db:
                import json
                tel = json.dumps({"router": router_used, "routing_ms": route_time, "ollama_ms": ollama_time, "telegram_received_ms": start_time*1000})
                
                # We'll use instruction 'continue' and set it to use the session. Wait, we don't have session_id in tasks table.
                # Let's alter tasks table or use telemetry field. We can use telemetry to pass session_id.
                tel_dict = json.loads(tel)
                tel_dict['session_id'] = session_id
                tel = json.dumps(tel_dict)
                
                await db.execute(
                    "INSERT INTO tasks (project_name, instruction, chat_id, message_id, status, telemetry) VALUES (?, ?, ?, ?, ?, ?)",
                    (active_proj, "Continue with the previous conversation context.", update.message.chat_id, update.message.message_id, "READY", tel)
                )
                await db.commit()
                async with db.execute("SELECT last_insert_rowid()") as cursor:
                    task_id = (await cursor.fetchone())[0]
                    
            await (update.message or update.callback_query.message).reply_html(f"✅ **Task added to queue** (ID: {task_id}) to continue session {session_id[:8]}")
            return
"""

if 'elif action == "continue_task":' not in main:
    main = main.replace('elif action == "clarify":', continue_logic + '\n        elif action == "clarify":')
    with open("app/main.py", "w") as f:
        f.write(main)
