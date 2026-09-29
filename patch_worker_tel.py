import re
with open("app/main.py", "r") as f:
    content = f.read()

bad = """                        await db.commit()
                        
                        start_time = datetime.now()
                        msg_text = ("""

good = """                        await db.commit()
                        
                        import time, json
                        start_time = datetime.now()
                        agent_start = time.time()
                        
                        # Read old telemetry
                        tel_json = task.get('telemetry')
                        tel = json.loads(tel_json) if tel_json else {}
                        
                        queue_wait = agent_start*1000 - tel.get('telegram_received_ms', agent_start*1000)
                        tel['queue_wait_ms'] = queue_wait
                        
                        msg_text = ("""

content = content.replace(bad, good)

bad2 = """                                    icon = "✅" if status == 'SUCCESS' else "🚨" if status == 'DEAD_LETTER' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s\"\"\""""
bad2_alt = """                                    icon = "✅" if status == 'SUCCESS' else "🚨" if status == 'DEAD_LETTER' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s\""""
bad2_actual = """                                    icon = "✅" if status == 'SUCCESS' else "🚨" if status == 'DEAD_LETTER' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s\""
                                    dur_str = dur_str[:-1]"""

# Just find the icon line
good2 = """                                    icon = "✅" if status == 'SUCCESS' else "🚨" if status == 'DEAD_LETTER' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"
                                    
                                    tel['agent_runtime_ms'] = (time.time() - agent_start) * 1000
                                    tel_str = json.dumps(tel)
                                    await db.execute("UPDATE tasks SET telemetry = ? WHERE id = ?", (tel_str, task_id))
                                    await db.commit()
"""

# replace carefully
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'icon = "✅" if status ==' in line:
        # replace next 2 lines
        lines[i] = good2
        lines[i+1] = ""
        lines[i+2] = ""

with open("app/main.py", "w") as f:
    f.write('\n'.join(lines))
