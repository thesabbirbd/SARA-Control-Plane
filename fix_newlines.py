with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace('f"⚠️ <b>Log unavailable</b>\n\nTask #{task_id} exists,\nbut its log file could not be found."', 'f"⚠️ <b>Log unavailable</b>\\n\\nTask #{task_id} exists,\\nbut its log file could not be found."')
content = content.replace('f"⚠️ <b>Log unavailable</b>\n\nTask #{task_id} log file is missing from disk."', 'f"⚠️ <b>Log unavailable</b>\\n\\nTask #{task_id} log file is missing from disk."')
content = content.replace('f"📎 <b>TASK #{task_id} LOG</b>\n\nProject:\n{row[\'project_name\']}\n\nFile:\n{log_file.name}\n\nSize:\n{log_file.stat().st_size / 1024:.1f} KB"', 'f"📎 <b>TASK #{task_id} LOG</b>\\n\\nProject:\\n{row[\'project_name\']}\\n\\nFile:\\n{log_file.name}\\n\\nSize:\\n{log_file.stat().st_size / 1024:.1f} KB"')
content = content.replace('f"{icon} <b>TASK #{task_id} {status}</b>\n\n<b>Result:</b>\n<pre>{log_content}</pre>"', 'f"{icon} <b>TASK #{task_id} {status}</b>\\n\\n<b>Result:</b>\\n<pre>{log_content}</pre>"')

with open("app/main.py", "w") as f:
    f.write(content)
