with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace('f"{icon} #{t[\'id\']}\n"', 'f"{icon} #{t[\'id\']}\\n"')
content = content.replace('f"Branch: {git_info[\'branch\']}\nWorking tree: {\'Clean\' if git_info[\'clean\'] else \'Modified\'}\nLatest commit: {git_info[\'commit\']}"', 'f"Branch: {git_info[\'branch\']}\\nWorking tree: {\'Clean\' if git_info[\'clean\'] else \'Modified\'}\\nLatest commit: {git_info[\'commit\']}"')
content = content.replace('f"📌 <b>PROJECT UPDATE</b>\n\n📁 <b>{project_name}</b>\n\n<b>Recent tasks:</b>\n{task_str}\n<b>Git:</b>\n{git_str}"', 'f"📌 <b>PROJECT UPDATE</b>\\n\\n📁 <b>{project_name}</b>\\n\\n<b>Recent tasks:</b>\\n{task_str}\\n<b>Git:</b>\\n{git_str}"')

with open("app/main.py", "w") as f:
    f.write(content)
