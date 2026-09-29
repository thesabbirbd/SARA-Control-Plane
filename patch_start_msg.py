import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                        msg_text = (
                            f"▶️ <b>Task #{task_id} STARTED</b>\\n\\n"
                            f"📁 <code>{project}</code>\\n"
                            f"🤖 Antigravity\\n\\n"
                            f"Started: {start_time.strftime('%H:%M:%S')}"
                        )"""

good = """                        msg_text = (
                            f"🚀 <b>TASK #{task_id} STARTED</b>\\n\\n"
                            f"📁 <code>{project}</code>\\n"
                            f"🤖 Antigravity\\n\\n"
                            f"Started: {start_time.strftime('%H:%M:%S')}\\n"
                            f"Live activity:\\nRunning..."
                        )"""

content = content.replace(bad, good)

# also add PID to msg after process is created
bad2 = """                                            process.stdout, log_file, ""
                                        ),
                                        stream_output("""

# wait, I can just append PID by editing the message. Let's see how process is started.
with open("app/main.py", "w") as f:
    f.write(content)
