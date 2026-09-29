import re
with open("app/main.py", "r") as f:
    content = f.read()

bad = """                            process = await asyncio.create_subprocess_exec(
                                AGY_BIN, "-p", instruction, "--output-format", "stream-json",
                                "--print-timeout", "30m", "--dangerously-skip-permissions",
                                cwd=str(project_dir),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                preexec_fn=os.setsid  # Put in its own process group
                            )"""

good = """                            agy_args = ["-p", instruction, "--output-format", "stream-json", "--print-timeout", "30m", "--dangerously-skip-permissions"]
                            if tel.get('session_id'):
                                agy_args.extend(["--conversation", tel['session_id']])
                                
                            process = await asyncio.create_subprocess_exec(
                                AGY_BIN, *agy_args,
                                cwd=str(project_dir),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                                preexec_fn=os.setsid  # Put in its own process group
                            )"""

content = content.replace(bad, good)
with open("app/main.py", "w") as f:
    f.write(content)
