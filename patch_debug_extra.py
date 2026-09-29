import re
with open("app/main.py", "r") as f:
    content = f.read()

debug_extra = """
    if args[0] == "session" and len(args) > 1:
        session_id = args[1]
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM agent_sessions WHERE id = ?", (session_id,)) as c:
                row = await c.fetchone()
        if not row:
            await update.message.reply_html("Session not found.")
            return
        msg = f"🔍 <b>DEBUG SESSION {session_id[:8]}</b>\\n\\nProject: {row['project_name']}\\nProvider: {row['provider']}\\nCreated: {row['created_at']}\\nLast Active: {row['last_active_at']}\\nStatus: {row['status']}"
        await update.message.reply_html(msg)
        return

    if args[0] == "workflow" and len(args) > 1:
        workflow_id = args[1]
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT id, status, instruction FROM tasks WHERE workflow_id = ? ORDER BY id ASC", (workflow_id,)) as c:
                rows = await c.fetchall()
        if not rows:
            await update.message.reply_html("Workflow not found.")
            return
        msg = f"🔍 <b>DEBUG WORKFLOW {workflow_id}</b>\\n\\n"
        for r in rows:
            msg += f"Task #{r['id']}: {r['status']} - {r['instruction'][:20]}...\\n"
        await update.message.reply_html(msg)
        return
"""

bad_debug = """    if args[0] == "task" and len(args) > 1:
        task_id = args[1]
    else:
        task_id = args[0]"""

good_debug = bad_debug + debug_extra

content = content.replace(bad_debug, good_debug)
with open("app/main.py", "w") as f:
    f.write(content)
