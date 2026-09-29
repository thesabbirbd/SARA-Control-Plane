## $(date +%Y-%m-%d) - Prevent Path Traversal in Project Names
**Vulnerability:** User-provided project names were directly concatenated with `BASE_DIR` (`BASE_DIR / project_name`) to form paths for file operations, git commands, and running subprocesses. This allowed path traversal using `../`.
**Learning:** In a DevOps bot, treating input project names as safe filesystem boundaries is dangerous.
**Prevention:** Always use `.resolve()` and `.is_relative_to(BASE_DIR)` to validate paths constructed from user input.
