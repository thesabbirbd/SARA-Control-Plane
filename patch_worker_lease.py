import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                        await transition_task(db, task_id, "STARTING")
                        await db.commit()"""

good = """                        async with db.execute("UPDATE tasks SET status = 'STARTING', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'PENDING'", (task_id,)) as update_cursor:
                            if update_cursor.rowcount == 0:
                                continue # Task was claimed by another worker or cancelled
                        await db.commit()"""

content = content.replace(bad, good)

with open("app/main.py", "w") as f:
    f.write(content)
