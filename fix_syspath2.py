with open("app/main.py", "r") as f:
    lines = f.readlines()

new_lines = []
imports = [
    "import sys\n",
    "import os\n",
    "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n"
]

for line in lines:
    if line not in imports:
        new_lines.append(line)

new_lines = imports + new_lines

with open("app/main.py", "w") as f:
    f.writelines(new_lines)
