import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                        async with db.execute("UPDATE tasks SET status = 'STARTING', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'PENDING'", (task_id,)) as update_cursor:
                            if update_cursor.rowcount == 0:
                                continue # Task was claimed by another worker or cancelled
                        await db.commit()"""

good = """                        async with db.execute("UPDATE tasks SET status = 'STARTING', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'PENDING'", (task_id,)) as update_cursor:
                            if update_cursor.rowcount == 0:
                                continue # Task was claimed by another worker or cancelled
                        
                        await db.execute("INSERT INTO executions (task_id, attempt, provider) VALUES (?, ?, ?)", (task_id, task['retry_count'] + 1, 'antigravity'))
                        async with db.execute("SELECT last_insert_rowid()") as cursor:
                            execution_id = (await cursor.fetchone())[0]
                        await db.commit()
                        
                        import sys
                        sys.path.append(str(Path(__file__).parent.parent))
                        from sara.events.bus import publish_event
                        await publish_event("TASK", task_id, "TASK_STARTED", {"execution_id": execution_id})
"""

content = content.replace(bad, good)

# Ensure publish_event logic is used later on
bad_complete = """                                    tel['agent_runtime_ms'] = (time.time() - agent_start) * 1000
                                    tel['telegram_send_ms'] = time.time() * 1000  # just a proxy
                                    tel_str = json.dumps(tel)
                                    await db.execute("UPDATE tasks SET telemetry = ? WHERE id = ?", (tel_str, task_id))
                                    await db.commit()"""
good_complete = """                                    tel['agent_runtime_ms'] = (time.time() - agent_start) * 1000
                                    tel['telegram_send_ms'] = time.time() * 1000  # just a proxy
                                    tel_str = json.dumps(tel)
                                    await db.execute("UPDATE tasks SET telemetry = ? WHERE id = ?", (tel_str, task_id))
                                    await db.execute("UPDATE executions SET status = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?", (status, execution_id))
                                    await db.commit()
                                    
                                    await publish_event("TASK", task_id, f"TASK_{status}", {"execution_id": execution_id, "duration_seconds": duration.seconds})"""

content = content.replace(bad_complete, good_complete)

with open("app/main.py", "w") as f:
    f.write(content)
