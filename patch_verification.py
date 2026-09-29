import re
with open("app/main.py", "r") as f:
    content = f.read()

bad = """                                    if status == 'DEAD_LETTER':"""
good = """                                    verification_cmd = task.get('verification_cmd') if 'verification_cmd' in task.keys() else None
                                    if status == 'SUCCESS' and verification_cmd:
                                        status = 'VERIFYING'
                                        await transition_task(db, task_id, status)
                                        await db.commit()
                                        
                                        import subprocess
                                        try:
                                            v_out = subprocess.check_output(verification_cmd, shell=True, cwd=str(project_dir), stderr=subprocess.STDOUT, text=True)
                                            status = 'SUCCESS'
                                        except subprocess.CalledProcessError as e:
                                            v_attempts = task.get('verification_attempts', 0) if 'verification_attempts' in task.keys() else 0
                                            if v_attempts < 3:
                                                # Auto-fix loop: Append failure context to instruction, and retry!
                                                new_instr = task['instruction'] + f"\\n\\n[VERIFICATION FAILED]\\nCommand: {verification_cmd}\\nExit code: {e.returncode}\\nOutput:\\n{e.output[:1000]}"
                                                await db.execute("UPDATE tasks SET instruction = ?, verification_attempts = verification_attempts + 1, status = 'READY' WHERE id = ?", (new_instr, task_id))
                                                await db.commit()
                                                continue # skip the rest of the finish block
                                            else:
                                                status = 'FAILED'
                                                await db.execute("UPDATE tasks SET error_message = ? WHERE id = ?", (f"Verification failed after 3 attempts: {e.output[:500]}", task_id))
                                                await db.commit()

                                    if status == 'DEAD_LETTER':"""

content = content.replace(bad, good)
with open("app/main.py", "w") as f:
    f.write(content)
