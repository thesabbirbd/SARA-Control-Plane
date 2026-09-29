with open("app/main.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.endswith('"\n') and 'text = "📋 <b>TASK CENTER</b>' in line:
        line = line.replace('\n', '\\n"\n')
        line = line.replace('"\\n"', '') # clean up
    elif line.endswith('"\n') and 'text += "▶️ <b>RUNNING</b>' in line:
        line = line.replace('\n', '\\n"\n')
        line = line.replace('"\\n"', '')
    elif line.endswith('"\n') and 'text += "⏳ <b>PENDING</b>' in line:
        line = line.replace('\n', '\\n"\n')
        line = line.replace('"\\n"', '')
    elif line.endswith('"\n') and 'text += "❌ <b>FAILED</b>' in line:
        line = line.replace('\n', '\\n"\n')
        line = line.replace('"\\n"', '')
    elif line.endswith('"\n') and 'text += "✅ <b>COMPLETED</b>' in line:
        line = line.replace('\n', '\\n"\n')
        line = line.replace('"\\n"', '')
    elif line.endswith('"\n') and 'text += "\\n' in line:
        line = line.replace('\n', 'n"\n')
        line = line.replace('"n"', '"')
    new_lines.append(line)

with open("app/main.py", "w") as f:
    f.writelines(new_lines)
