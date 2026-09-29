import re

with open("app/main.py", "r") as f:
    content = f.read()

new_handlers = """    if data.startswith("retry_"):
        task_id = data.split("_")[1]
        context.args = [task_id]
        await retry_command(update, context)
        
    elif data.startswith("cancel_"):
        task_id = data.split("_")[1]
        context.args = [task_id]
        await cancel_command(update, context)
        
    elif data.startswith("result_"):
        task_id = data.split("_")[1]
        await task_result_command(update, context, task_id)
        
    elif data.startswith("log_"):
        task_id = data.split("_")[1]
        await send_log_command(update, context, task_id)"""

content = re.sub(r"    if data\.startswith\(\"retry_\"\):.*?await cancel_command\(update, context\)", new_handlers, content, flags=re.DOTALL)

with open("app/main.py", "w") as f:
    f.write(content)
