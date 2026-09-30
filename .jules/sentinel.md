## $(date +%Y-%m-%d) - Prevent Path Traversal in Project Names
**Vulnerability:** User-provided project names were directly concatenated with `BASE_DIR` (`BASE_DIR / project_name`) to form paths for file operations, git commands, and running subprocesses. This allowed path traversal using `../`.
**Learning:** In a DevOps bot, treating input project names as safe filesystem boundaries is dangerous.
**Prevention:** Always use `.resolve()` and `.is_relative_to(BASE_DIR)` to validate paths constructed from user input.
## $(date +%Y-%m-%d) - Command Injection in Verification Flow
**Vulnerability:** In `app/main.py`, `verification_cmd` was executed using `subprocess.check_output(verification_cmd, shell=True)`, which poses a severe command injection risk since it relies on `shell=True`. Additionally, synchronous execution blocked the asyncio event loop.
**Learning:** `shell=True` should never be used with unsanitized dynamic input. Synchronous process execution should also be avoided within an async block as it starves the loop.
**Prevention:** Use `shlex.split()` to securely parse the command into an arguments array, and execute it using `asyncio.create_subprocess_exec()` to avoid blocking the event loop while avoiding command injection.
