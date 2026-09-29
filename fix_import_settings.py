with open("app/main.py", "r") as f:
    content = f.read()

content = "from sara.config.settings import settings\n" + content

with open("app/main.py", "w") as f:
    f.write(content)
