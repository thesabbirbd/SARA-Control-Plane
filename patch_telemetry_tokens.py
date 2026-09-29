import re
with open("app/main.py", "r") as f:
    content = f.read()

bad = """                                                try:
                                                    parsed = json.loads(line)
                                                    if parsed.get('type') == 'result':
                                                        result_str = parsed.get("response")
                                                        if result_str:
                                                            await db.execute("UPDATE tasks SET result = ? WHERE id = ?", (result_str, task_id))
                                                            await db.commit()
                                                            break
                                                except: pass"""

good = """                                                try:
                                                    parsed = json.loads(line)
                                                    if parsed.get('type') == 'result':
                                                        result_str = parsed.get("response")
                                                        if result_str:
                                                            await db.execute("UPDATE tasks SET result = ? WHERE id = ?", (result_str, task_id))
                                                        usage = parsed.get('usage', {})
                                                        if usage:
                                                            tel['input_tokens'] = usage.get('input_tokens', 0)
                                                            tel['output_tokens'] = usage.get('output_tokens', 0)
                                                            tel['cached_tokens'] = usage.get('cached_tokens', 0)
                                                            await db.execute("UPDATE tasks SET telemetry = ? WHERE id = ?", (json.dumps(tel), task_id))
                                                        await db.commit()
                                                        break
                                                except: pass"""

content = content.replace(bad, good)
with open("app/main.py", "w") as f:
    f.write(content)
