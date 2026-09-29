import os

MAIN_FILE = "/home/thesabbir/Documents/RPA Projects/sabbiR-control-plane/app/main.py"

with open(MAIN_FILE, "r") as f:
    code = f.read()

# 1. Add `is_process_alive`
helpers = """
def is_process_alive(pid: int) -> bool:
    if not pid: return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
"""
if "def is_process_alive" not in code:
    code = code.replace("def authorized(update: Update) -> bool:", helpers + "\ndef authorized(update: Update) -> bool:")


# 2. Add `stale_task_recovery` and `startup_recovery`
recovery_code = """
async def startup_recovery():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE status IN ('RUNNING', 'STARTING')") as cursor:
            tasks = await cursor.fetchall()
            
        for t in tasks:
            if not is_process_alive(t['pid']):
                await db.execute("UPDATE tasks SET status = 'INTERRUPTED' WHERE id = ?", (t['id'],))
        await db.commit()

async def stale_task_recovery():
    while True:
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM tasks WHERE status = 'RUNNING'") as cursor:
                    tasks = await cursor.fetchall()
                for t in tasks:
                    if not is_process_alive(t['pid']):
                        await db.execute("UPDATE tasks SET status = 'INTERRUPTED' WHERE id = ?", (t['id'],))
                await db.commit()
        except Exception as e:
            print("Stale recovery error:", e)
        await asyncio.sleep(10)
"""
if "async def startup_recovery" not in code:
    code = code.replace("async def init_db():", recovery_code + "\nasync def init_db():")


# 3. Modify `post_init`
post_init_old = """async def post_init(app: Application):
    await init_db()
    scheduler.start()
    asyncio.create_task(background_worker())"""
post_init_new = """async def post_init(app: Application):
    await init_db()
    await startup_recovery()
    scheduler.start()
    asyncio.create_task(stale_task_recovery())
    asyncio.create_task(background_worker())"""
code = code.replace(post_init_old, post_init_new)


# 4. Modify init_db (remove the old naive INTERRUPTED update)
init_db_old = """        await db.execute("UPDATE tasks SET status = 'INTERRUPTED' WHERE status = 'RUNNING'")
        await db.commit()"""
init_db_new = """        await db.commit()"""
code = code.replace(init_db_old, init_db_new)


# 5. Replace `cancel_command`
cancel_old_idx = code.find("async def cancel_command(")
cancel_end_idx = code.find("async def retry_command(", cancel_old_idx)
cancel_new = """async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/cancel &lt;id&gt;</code>")
        return
    task_id = context.args[0]
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            task = await cursor.fetchone()
            
    if not task:
        await update.message.reply_html(f"❌ Task <b>#{task_id}</b> not found.")
        return
        
    if task['status'] not in ['PENDING', 'STARTING', 'RUNNING']:
        await update.message.reply_html(f"⚠️ Task #{task_id} is already <b>{task['status']}</b>.")
        return
        
    async with aiosqlite.connect(DB_PATH) as db:
        if task['pid'] and is_process_alive(task['pid']):
            try:
                # Kill process group
                os.killpg(os.getpgid(task['pid']), signal.SIGTERM)
                await asyncio.sleep(1)
                if is_process_alive(task['pid']):
                    os.killpg(os.getpgid(task['pid']), signal.SIGKILL)
            except Exception as e:
                pass
        
        await db.execute("UPDATE tasks SET status = 'CANCELLED' WHERE id = ?", (task_id,))
        await db.commit()
        
    await update.message.reply_html(f"🛑 Task <b>#{task_id}</b> cancelled safely.")

"""
code = code[:cancel_old_idx] + cancel_new + code[cancel_end_idx:]


# 6. Replace `retry_command`
retry_old_idx = code.find("async def retry_command(")
retry_end_idx = code.find("async def health(", retry_old_idx)
retry_new = """async def retry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not context.args:
        await update.message.reply_html("Usage: <code>/retry &lt;id&gt;</code>")
        return
    task_id = context.args[0]
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            task = await cursor.fetchone()
            
    if not task:
        await update.message.reply_html(f"❌ Task <b>#{task_id}</b> not found.")
        return
        
    if task['status'] in ['PENDING', 'RUNNING', 'STARTING']:
        await update.message.reply_html(f"⚠️ Task #{task_id} is currently <b>{task['status']}</b>. Cannot retry.")
        return
        
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tasks (project_name, instruction, status, parent_task_id) VALUES (?, ?, 'PENDING', ?)",
            (task['project_name'], task['instruction'], task['id'])
        )
        new_id = cursor.lastrowid
        await db.commit()
        
    await update.message.reply_html(f"🔁 <b>Task Queued for Retry</b>\\nOld Task: #{task_id}\\nNew Task: #{new_id}\\n\\n<i>Worker will pick this up shortly.</i>")

"""
code = code[:retry_old_idx] + retry_new + code[retry_end_idx:]


# 7. Replace `background_worker`
worker_old_idx = code.find("async def background_worker():")
worker_end_idx = code.find("async def post_init(", worker_old_idx)
worker_new = """async def background_worker():
    print("Background worker started.")
    
    # Ensure logs directory
    LOGS_DIR = BASE_DIR.parent / "sabbiR-control-plane" / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    while True:
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                # Safety check: don't start new if one is RUNNING
                async with db.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('STARTING', 'RUNNING')") as cursor:
                    active = (await cursor.fetchone())[0]
                    
                if active == 0:
                    async with db.execute("SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY created_at ASC LIMIT 1") as cursor:
                        task = await cursor.fetchone()
                    
                    if task:
                        task_id = task['id']
                        project = task['project_name']
                        instruction = task['instruction']
                        
                        await db.execute("UPDATE tasks SET status = 'STARTING', started_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
                        await db.commit()
                        
                        start_time = datetime.now()
                        msg_text = (
                            f"▶️ <b>Task #{task_id} STARTED</b>\\n\\n"
                            f"📁 <code>{project}</code>\\n"
                            f"🤖 Antigravity\\n\\n"
                            f"Started: {start_time.strftime('%H:%M:%S')}"
                        )
                        if task['parent_task_id']:
                            msg_text += f"\\n🔁 <i>Retry of Task #{task['parent_task_id']}</i>"
                            
                        await bot_app.bot.send_message(
                            chat_id=ALLOWED_USER_ID,
                            text=msg_text,
                            parse_mode="HTML"
                        )
                        
                        project_dir = BASE_DIR / project
                        log_file_path = LOGS_DIR / f"task_{task_id}.log"
                        
                        await db.execute("UPDATE tasks SET log_path = ? WHERE id = ?", (str(log_file_path), task_id))
                        await db.commit()
                        
                        if not project_dir.exists():
                            await db.execute("UPDATE tasks SET status = 'FAILED', error_message = ? WHERE id = ?", (f"Project not found: {project_dir}", task_id))
                            await db.commit()
                            continue
                            
                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"\\n\\n--- STARTING TASK #{task_id} AT {datetime.now()} ---\\n")
                            log_file.write(f"Project: {project}\\nInstruction: {instruction}\\n")
                            log_file.flush()
                            
                            process = await asyncio.create_subprocess_exec(
                                AGY_BIN, "-p", instruction, "--output-format", "json",
                                "--print-timeout", "30m", "--dangerously-skip-permissions",
                                cwd=str(project_dir),
                                stdout=log_file,
                                stderr=log_file,
                                preexec_fn=os.setsid  # Put in its own process group
                            )
                            
                            await db.execute("UPDATE tasks SET status = 'RUNNING', pid = ? WHERE id = ?", (process.pid, task_id))
                            await db.commit()
                            
                            # Update PID in message
                            await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"🔧 Task #{task_id} PID: <code>{process.pid}</code>", parse_mode="HTML")
                            
                            # Wait for it, but allow timeouts and cancellations
                            try:
                                # 30 min timeout
                                await asyncio.wait_for(process.wait(), timeout=1800)
                                exit_code = process.returncode
                                
                                async with db.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)) as c:
                                    curr = await c.fetchone()
                                    
                                if curr and curr['status'] == 'CANCELLED':
                                    pass # Handled by cancel_command
                                else:
                                    status = 'SUCCESS' if exit_code == 0 else 'FAILED'
                                    await db.execute("UPDATE tasks SET status = ?, exit_code = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?", (status, exit_code, task_id))
                                    await db.commit()
                                    
                                    icon = "✅" if status == 'SUCCESS' else "❌"
                                    duration = datetime.now() - start_time
                                    dur_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"
                                    
                                    fin_text = (
                                        f"{icon} <b>Task #{task_id} COMPLETED</b>\\n\\n"
                                        f"Duration: {dur_str}\\n"
                                        f"Exit code: {exit_code}\\n"
                                        f"Log: <code>{log_file_path.name}</code>"
                                    )
                                    keyboard = [[InlineKeyboardButton("🔁 Retry", callback_data=f"retry_{task_id}")]] if status != 'SUCCESS' else []
                                    await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=fin_text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None, parse_mode="HTML")
                                    
                            except asyncio.TimeoutError:
                                # Timeout triggered
                                try:
                                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                                    await asyncio.sleep(1)
                                    if is_process_alive(process.pid):
                                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                                except Exception:
                                    pass
                                    
                                await db.execute("UPDATE tasks SET status = 'TIMEOUT', finished_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
                                await db.commit()
                                
                                await bot_app.bot.send_message(
                                    chat_id=ALLOWED_USER_ID, 
                                    text=f"⏱ <b>Task #{task_id} TIMEOUT</b>\\n\\n30-minute execution limit reached.\\nProcess terminated safely.", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Retry", callback_data=f"retry_{task_id}")]]),
                                    parse_mode="HTML"
                                )
                                
        except Exception as e:
            print(f"Worker error: {e}")
            
        await asyncio.sleep(3)

"""
code = code[:worker_old_idx] + worker_new + code[worker_end_idx:]

with open(MAIN_FILE, "w") as f:
    f.write(code)

print("Patching complete.")
