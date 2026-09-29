import re
with open("app/main.py", "r") as f:
    content = f.read()

dep_code = """
async def update_task_states():
    while True:
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                # Mark as READY if dependencies met
                await db.execute('''
                    UPDATE tasks 
                    SET status = 'READY' 
                    WHERE status IN ('PENDING', 'BLOCKED_BY_DEPENDENCY')
                    AND (depends_on IS NULL OR depends_on IN (SELECT id FROM tasks WHERE status = 'SUCCESS'))
                ''')
                # Mark as BLOCKED_BY_DEPENDENCY if dependencies not met
                await db.execute('''
                    UPDATE tasks 
                    SET status = 'BLOCKED_BY_DEPENDENCY' 
                    WHERE status IN ('PENDING', 'READY')
                    AND depends_on IS NOT NULL 
                    AND depends_on NOT IN (SELECT id FROM tasks WHERE status = 'SUCCESS')
                ''')
                await db.commit()
        except: pass
        await asyncio.sleep(5)
"""

content = content.replace("async def stale_task_recovery():", dep_code + "\nasync def stale_task_recovery():")
content = content.replace("asyncio.create_task(stale_task_recovery())", "asyncio.create_task(stale_task_recovery())\n    asyncio.create_task(update_task_states())")

# Update worker query to fetch from 'READY' instead of 'PENDING'
bad_query = "SELECT * FROM tasks WHERE status = 'PENDING' AND (next_attempt IS NULL OR next_attempt <= CURRENT_TIMESTAMP) AND (depends_on IS NULL OR depends_on IN (SELECT id FROM tasks WHERE status = 'SUCCESS')) ORDER BY CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'normal' THEN 3 WHEN 'low' THEN 4 ELSE 3 END, created_at ASC LIMIT 1"
good_query = "SELECT * FROM tasks WHERE status = 'READY' AND (next_attempt IS NULL OR next_attempt <= CURRENT_TIMESTAMP) ORDER BY CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'normal' THEN 3 WHEN 'low' THEN 4 ELSE 3 END, created_at ASC LIMIT 1"
content = content.replace(bad_query, good_query)

# Update lease query
bad_lease = "UPDATE tasks SET status = 'STARTING', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'PENDING'"
good_lease = "UPDATE tasks SET status = 'STARTING', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'READY'"
content = content.replace(bad_lease, good_lease)

with open("app/main.py", "w") as f:
    f.write(content)
