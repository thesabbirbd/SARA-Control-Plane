import re

with open("app/main.py", "r") as f:
    content = f.read()

# Replace config
content = re.sub(
    r"BOT_TOKEN = os\.getenv\('TELEGRAM_BOT_TOKEN'\)\nALLOWED_USER_IDS = \[.*?\]\nOLLAMA_BASE_URL = os\.getenv\('OLLAMA_BASE_URL', 'http://127.0.0.1:11434'\)\nOLLAMA_MODEL = os\.getenv\('OLLAMA_MODEL', 'llama3'\)",
    "from sara.config.settings import settings",
    content, flags=re.DOTALL
)

content = content.replace("BOT_TOKEN", "settings.telegram_bot_token")
content = content.replace("ALLOWED_USER_IDS", "settings.telegram_allowed_user_ids")
content = content.replace("OLLAMA_BASE_URL", "settings.ollama_base_url")
content = content.replace("OLLAMA_MODEL", "settings.ollama_model")
content = content.replace("PROJECTS_ROOT = Path.home() / 'Documents' / 'RPA Projects'", "")
content = content.replace("PROJECTS_ROOT", "settings.workspace_roots[0]")

# Add risk classification
content = content.replace("import subprocess", "import subprocess\nfrom sara.security.risk import classify_command, RiskLevel\nfrom sara.security.redaction import redact")

with open("app/main.py", "w") as f:
    f.write(content)
