import re
with open("app/main.py", "r") as f:
    content = f.read()

bad = """                                        event_type = event.get('type')
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
                                                live_act = f"⏳ {event.get('status', 'Thinking')}\""""

good = """                                        event_type = event.get('event') or event.get('type')
                                        
                                        if event_type == 'init':
                                            conv_id = event.get('conversation_id')
                                            if conv_id:
                                                # Save session_id
                                                await db.execute("UPDATE executions SET session_id = ? WHERE id = ?", (conv_id, execution_id))
                                                await db.execute("INSERT INTO agent_sessions (id, project_name, provider) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET last_active_at = CURRENT_TIMESTAMP", (conv_id, project, 'antigravity'))
                                                await db.commit()
                                        
                                        if event_type:
                                            sara_evt = "AGENT_OUTPUT"
                                            if event_type == "init": sara_evt = "AGENT_STARTED"
                                            elif event_type == "step_update": sara_evt = "AGENT_STEP"
                                            elif event_type == "tool_call": sara_evt = "AGENT_TOOL"
                                            
                                            await publish_event("EXECUTION", execution_id, sara_evt, event)
                                            
                                        now = time.time()
                                        if now - last_edit > throttle and start_msg_obj:
                                            last_edit = now
                                            
                                            live_act = "Running..."
                                            if event_type == "step_update":
                                                su = event.get('step_update', {})
                                                st = su.get('step_type', 'unknown')
                                                live_act = f"🔧 Action: {st}"
                                            elif event_type == "text":
                                                live_act = f"💬 Outputting text..."
                                            elif event_type == "result":
                                                live_act = f"✅ Finishing..."
                                            """

content = content.replace(bad, good)

bad_result = """                                                    if parsed.get('type') == 'result':"""
good_result = """                                                    if parsed.get('event') == 'result' or parsed.get('type') == 'result':"""

content = content.replace(bad_result, good_result)

with open("app/main.py", "w") as f:
    f.write(content)
