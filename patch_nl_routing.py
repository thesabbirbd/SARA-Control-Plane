import re

with open("app/main.py", "r") as f:
    content = f.read()

router_block = """    if intent:
        action = intent.get("action")
        if action == "greeting":
            await greeting_command(update, context)
            return
        elif action == "cancel_all":
            await cancel_all_command(update, context)
            return
        elif action == "ollama_status":
            await ollama_status_command(update, context)
            return
        elif action == "list_tasks":
            await tasks_command(update, context)
            return
        elif action == "project_update":
            await project_update_command(update, context, active_proj)
            return
        elif action == "task_status":
            # Just route to result for now
            await task_result_command(update, context, intent.get("task_id"))
            return
        elif action == "send_log":
            await send_log_command(update, context, intent.get("task_id"))
            return
        elif action == "task_result":
            await task_result_command(update, context, intent.get("task_id"))
            return
        elif action == "send_latest_log":
            await send_latest_log_command(update, context)
            return"""

content = re.sub(r"    if intent:.*?elif action == \"send_latest_log\":\n            await send_latest_log_command\(update, context\)\n            return", router_block, content, flags=re.DOTALL)

with open("app/main.py", "w") as f:
    f.write(content)
