with open("sara/config/settings.py", "r") as f:
    content = f.read()

content = "from dotenv import load_dotenv\nload_dotenv()\n" + content

with open("sara/config/settings.py", "w") as f:
    f.write(content)
