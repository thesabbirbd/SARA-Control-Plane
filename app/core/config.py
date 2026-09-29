import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.environ.get("TELEGRAM_ALLOWED_USER_ID", 0))
AGY_BIN = os.getenv("ANTIGRAVITY_BIN", "agy")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:2b")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
DB_PATH = os.environ.get("SARA_DB_PATH", os.path.join(PROJECT_ROOT, "queue.db"))
BASE_DIR = Path(os.environ.get("SARA_PROJECTS_DIR", os.path.dirname(PROJECT_ROOT))).expanduser().resolve()
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
BASE_DIR.mkdir(parents=True, exist_ok=True)
