# SARA Control Plane
**Self-hosted Agent Relay & Automation Platform**

SARA is a self-hosted orchestration platform designed to securely manage, route, and execute autonomous AI agent workflows (using Antigravity, Gemini, Codex, Ollama) via Telegram, CLI, and Web. 

It provides persistent queues, structured observability, and a local-first control plane for your agentic coding sessions.

## 🚀 Key Features
- **Telegram-First Control:** Manage your agents and automation from anywhere via Telegram.
- **Provider Agnostic:** Designed to integrate with Google Antigravity (AGY), Gemini, Codex, and local LLMs (Ollama).
- **Deterministic Routing:** Reliable command parsing before falling back to natural language intents.
- **Persistent Queue System:** SQLite-backed task scheduling and lifecycle management.
- **Deep Observability:** Tmux-powered live console, robust per-task logging, and process-group isolation.
- **Privacy By Default:** Your code, tokens, and data stay on your machine.

## 🛠 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/thesabbirbd/SARA-Control-Plane.git
cd SARA-Control-Plane
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Telegram Bot Token, User ID, and preferred paths
nano .env
```

### 3. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run SARA
```bash
python app/main.py
```
*Note: For production, we recommend setting up `sara.service` using systemd.*

## 📈 Roadmap
For detailed milestones and upcoming features, see [ROADMAP.md](ROADMAP.md).

## 🔒 Security Model
- **User-Locked Authorization:** Only whitelisted Telegram User IDs can execute commands.
- **Local Isolation:** No cloud dashboards. The control plane runs entirely on your local infrastructure.

---
*Developed by thesabbirbd.*
