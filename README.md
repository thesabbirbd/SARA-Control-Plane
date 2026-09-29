# S.A.R.A. Control Plane 🚀
**Self-hosted Agent Relay & Automation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/YOUR-USERNAME/sara-control-plane/graphs/commit-activity)

> **Control your local AI coding agents from anywhere.**

**SARA** is an advanced, Telegram-first, local-first control plane designed to orchestrate AI coding agents, background tasks, schedulers, and developer workflows. Instead of being locked into a single ecosystem, SARA acts as a provider-agnostic bridge—routing your natural language commands to the right agents (Antigravity, Gemini, Codex, Ollama) while maintaining strict local queues and session states.

### 🛡️ The Core Promise
**Your machine. Your projects. Your agents. Your credentials. Your control.**

No centralized servers, no shared tokens, and no forced cloud dependency. SARA runs entirely on your local machine or server, ensuring your source code and environments remain 100% private.

### ✨ Key Capabilities
- **📱 Telegram-First UI:** Interactive dashboards, inline task controls, and natural language routing right from your phone.
- **🤖 Provider Agnostic:** Plug-and-play support for Google Antigravity, Gemini API, Ollama, and more.
- **🔄 Robust Task Engine:** Built-in SQLite queue, priority handling, exponential backoff retries, and overnight batch execution.
- **⏰ Advanced Scheduling:** Natural-language scheduling and APScheduler integration for cron-like developer tasks.
- **🔒 Security by Default:** Workspace allowlists, non-root execution policies, Git safety rules, and secret redaction.

---
*Built with ❤️ by **THE SABBiR***

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
