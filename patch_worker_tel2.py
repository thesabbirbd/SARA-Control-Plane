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
                        
                        tel_json = task['telemetry'] if 'telemetry' in task.keys() else None
                        tel = json.loads(tel_json) if tel_json else {}
                        queue_wait = agent_start*1000 - tel.get('telegram_received_ms', agent_start*1000)
                        tel['queue_wait_ms'] = queue_wait
                        
                        msg_text = ("""

content = content.replace(bad, good)

bad2 = """                                    icon = "✅" if status == 'SUCCESS' else "🚨" if status == 'DEAD_LETTER' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s\"\"\""""

# Let's find exactly the line in background_worker
start_idx = content.find("async def background_worker(")
if start_idx == -1:
    start_idx = content.find("async def background_worker")

sub_idx = content.find('icon = "✅" if status == \'SUCCESS\' else "🚨" if status == \'DEAD_LETTER\' else "❌"', start_idx)
if sub_idx != -1:
    # We want to insert our telemetry save right after `dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"`
    dur_idx = content.find('dur_str =', sub_idx)
    nl_idx = content.find('\n', dur_idx)
    
    insert = """
                                    tel['agent_runtime_ms'] = (time.time() - agent_start) * 1000
                                    tel['telegram_send_ms'] = time.time() * 1000  # just a proxy
                                    tel_str = json.dumps(tel)
                                    await db.execute("UPDATE tasks SET telemetry = ? WHERE id = ?", (tel_str, task_id))
                                    await db.commit()"""
    content = content[:nl_idx] + insert + content[nl_idx:]

with open("app/main.py", "w") as f:
    f.write(content)
