import re

with open("app/main.py", "r") as f:
    content = f.read()

bad = """                        # Helper to stream output
                        async def stream_output(stream, log_file, prefix=""):
                            async for line in stream:
                                decoded = line.decode('utf-8', errors='replace')
                                log_file.write(decoded)
                                log_file.flush()
                                os.fsync(log_file.fileno())
                                print(f"{prefix}{decoded}", end="", flush=True)

                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"\\n\\n--- STARTING TASK #{task_id} AT {datetime.now()} ---\\n")
                            log_file.write(f"Project: {project}\\nInstruction: {instruction}\\n")
                            log_file.flush()
                            
                            process = await asyncio.create_subprocess_exec(
                                AGY_BIN, "-p", instruction, "--output-format", "json",
                                "--print-timeout", "30m", "--dangerously-skip-permissions",
                                cwd=str(project_dir),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                preexec_fn=os.setsid  # Put in its own process group
                            )
                            
                            await transition_task(db, task_id, "RUNNING", pid=process.pid)
                            await db.commit()
                            
                            try:
                                msg_text = msg_text.replace("Running...", f"PID:\\n{process.pid}\\n\\nLive activity:\\nRunning...")
                                await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=msg_text, parse_mode="HTML")
                            except: pass
                            
                            # Update PID in message
                            await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=f"🔧 Task #{task_id} PID: <code>{process.pid}</code>", parse_mode="HTML")"""

good = """                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"\\n\\n--- STARTING TASK #{task_id} AT {datetime.now()} ---\\n")
                            log_file.write(f"Project: {project}\\nInstruction: {instruction}\\n")
                            log_file.flush()
                            
                            process = await asyncio.create_subprocess_exec(
                                AGY_BIN, "-p", instruction, "--output-format", "stream-json",
                                "--print-timeout", "30m", "--dangerously-skip-permissions",
                                cwd=str(project_dir),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                preexec_fn=os.setsid  # Put in its own process group
                            )
                            
                            await transition_task(db, task_id, "RUNNING", pid=process.pid)
                            await db.commit()
                            
                            start_msg_obj = None
                            try:
                                msg_text = msg_text.replace("Running...", f"PID:\\n{process.pid}\\n\\nLive activity:\\nRunning...")
                                start_msg_obj = await bot_app.bot.send_message(chat_id=ALLOWED_USER_ID, text=msg_text, parse_mode="HTML")
                            except: pass
                            
                            # Helper to stream output
                            async def stream_output(stream, log_file, prefix=""):
                                import time, json
                                last_edit = time.time()
                                throttle = 15.0 # seconds
                                
                                async for line in stream:
                                    decoded = line.decode('utf-8', errors='replace')
                                    log_file.write(decoded)
                                    log_file.flush()
                                    os.fsync(log_file.fileno())
                                    print(f"{prefix}{decoded}", end="", flush=True)
                                    
                                    try:
                                        if not decoded.strip(): continue
                                        event = json.loads(decoded)
                                        import sys
                                        sys.path.append(str(Path(__file__).parent.parent))
                                        from sara.events.bus import publish_event
                                        
                                        event_type = event.get('type')
                                        if event_type:
                                            # Normalize event type mapping
                                            sara_evt = "AGENT_OUTPUT"
                                            if event_type == "init": sara_evt = "AGENT_STARTED"
                                            elif event_type == "step": sara_evt = "AGENT_STEP"
                                            elif event_type == "tool_call": sara_evt = "AGENT_TOOL"
                                            
                                            await publish_event("EXECUTION", execution_id, sara_evt, event)
                                            
                                        now = time.time()
                                        if now - last_edit > throttle and start_msg_obj:
                                            last_edit = now
                                            
                                            live_act = "Running..."
                                            if event_type == "tool_call":
                                                tool_name = event.get('tool_call', {}).get('name', 'unknown')
                                                live_act = f"🔧 Running:\\n{tool_name}"
                                            elif event_type == "text":
                                                live_act = f"💬 Outputting text..."
                                            elif event_type == "status":
                                                live_act = f"⏳ {event.get('status', 'Thinking')}"
                                            
                                            dur = int(now - agent_start)
                                            dur_str = f"{dur // 60}m {dur % 60}s"
                                            
                                            new_text = (
                                                f"🚀 <b>TASK #{task_id} RUNNING</b>\\n\\n"
                                                f"📁 <code>{project}</code>\\n"
                                                f"🤖 Antigravity\\n\\n"
                                                f"PID: {process.pid}\\n"
                                                f"Elapsed: {dur_str}\\n\\n"
                                                f"Live activity:\\n{live_act}"
                                            )
                                            try:
                                                await bot_app.bot.edit_message_text(chat_id=ALLOWED_USER_ID, message_id=start_msg_obj.message_id, text=new_text, parse_mode="HTML")
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass"""

content = content.replace(bad, good)

# Also update the final parsing logic to handle stream-json
# Stream json result has type="result"
bad_result = """                                    # Attempt to parse last line as JSON for result
                                    result_str = None
                                    try:
                                        with open(log_file_path, "r") as lf:
                                            lines = lf.readlines()
                                            if lines:
                                                import json
                                                last_line = lines[-1].strip()
                                                parsed = json.loads(last_line)
                                                result_str = parsed.get("response")
                                                if result_str:
                                                    await db.execute("UPDATE tasks SET result = ? WHERE id = ?", (result_str, task_id))
                                                    await db.commit()
                                    except Exception:
                                        pass"""

good_result = """                                    # Attempt to parse stream-json for result
                                    result_str = None
                                    try:
                                        with open(log_file_path, "r") as lf:
                                            import json
                                            for line in reversed(lf.readlines()):
                                                line = line.strip()
                                                if not line: continue
                                                try:
                                                    parsed = json.loads(line)
                                                    if parsed.get('type') == 'result':
                                                        result_str = parsed.get("response")
                                                        if result_str:
                                                            await db.execute("UPDATE tasks SET result = ? WHERE id = ?", (result_str, task_id))
                                                            await db.commit()
                                                            break
                                                except: pass
                                    except Exception:
                                        pass"""

content = content.replace(bad_result, good_result)

with open("app/main.py", "w") as f:
    f.write(content)
