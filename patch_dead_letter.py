import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                                        else:
                                            await transition_task(db, task_id, status, exit_code=exit_code)
                                            await db.commit()"""

good = """                                        else:
                                            status = 'DEAD_LETTER'
                                            await transition_task(db, task_id, status, exit_code=exit_code)
                                            await db.commit()"""

content = content.replace(bad, good)

# also update icon mapping
content = content.replace('icon = "✅" if status == \'SUCCESS\' else "❌"', 'icon = "✅" if status == \'SUCCESS\' else "🚨" if status == \'DEAD_LETTER\' else "❌"')

with open("app/main.py", "w") as f:
    f.write(content)
