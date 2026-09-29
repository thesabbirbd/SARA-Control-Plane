with open("app/main.py", "r") as f:
    content = f.read()

workflow_handler = """
async def workflow_command(update, context):
    if not authorized(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_html("Usage: <code>/workflow &lt;project&gt; &lt;plan_file.md&gt;</code>")
        return
        
    project = args[0]
    plan_file = " ".join(args[1:])
    
    import uuid
    workflow_id = str(uuid.uuid4())[:8]
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Read plan (mock reading logic, since in reality we'd parse the markdown)
        tasks_to_create = [
            f"Read {plan_file} and extract objective 1",
            "Implement objective 1 based on previous research",
            "Run tests for objective 1 and fix any issues"
        ]
        
        prev_id = None
        for i, task_instr in enumerate(tasks_to_create):
            await db.execute(
                "INSERT INTO tasks (project_name, instruction, chat_id, message_id, status, depends_on, workflow_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project, task_instr, update.message.chat_id, update.message.message_id, "PENDING", prev_id, workflow_id)
            )
            async with db.execute("SELECT last_insert_rowid()") as c:
                prev_id = (await c.fetchone())[0]
        await db.commit()
        
    await update.message.reply_html(f"📦 <b>WORKFLOW #{workflow_id} CREATED</b>\\n\\nProject: {project}\\nFile: {plan_file}\\nTasks created: {len(tasks_to_create)}\\n\\nExecution will proceed sequentially.")

"""

if "async def workflow_command" not in content:
    content = content.replace("async def help_command", workflow_handler + "\nasync def help_command")
    with open("app/main.py", "w") as f:
        f.write(content)
