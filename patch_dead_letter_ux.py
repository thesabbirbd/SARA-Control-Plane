import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                                    fin_text = (
                                        f"{icon} <b>TASK #{task_id} COMPLETED</b>\\n\\n"
                                        f"📁 <b>Project</b>\\n{project}\\n\\n"
                                        f"🤖 <b>Agent</b>\\nAntigravity\\n\\n"
                                        f"⏱ <b>Duration</b>\\n{dur_str}\\n\\n"
                                    )"""

good = """                                    if status == 'DEAD_LETTER':
                                        fin_text = (
                                            f"🚨 <b>TASK #{task_id} MOVED TO DEAD LETTER</b>\\n\\n"
                                            f"📁 <b>Project</b>\\n{project}\\n\\n"
                                            f"<b>Reason:</b>\\nRepeated execution failure.\\n\\n"
                                            f"<b>Attempts:</b>\\n3\\n\\n"
                                            f"The task was NOT executed again.\\n\\n"
                                        )
                                    else:
                                        status_word = 'COMPLETED' if status == 'SUCCESS' else status
                                        fin_text = (
                                            f"{icon} <b>TASK #{task_id} {status_word}</b>\\n\\n"
                                            f"📁 <b>Project</b>\\n{project}\\n\\n"
                                            f"🤖 <b>Agent</b>\\nAntigravity\\n\\n"
                                            f"⏱ <b>Duration</b>\\n{dur_str}\\n\\n"
                                        )"""

content = content.replace(bad, good)

with open("app/main.py", "w") as f:
    f.write(content)
