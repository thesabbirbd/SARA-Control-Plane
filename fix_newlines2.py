with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace('log_content = log_content[-1000:] + "\n...(truncated)"', 'log_content = log_content[-1000:] + "\\n...(truncated)"')
with open("app/main.py", "w") as f:
    f.write(content)
