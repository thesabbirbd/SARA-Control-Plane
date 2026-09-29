import re

with open("app/main.py", "r") as f:
    content = f.read()

worker_start = content.find("async def background_worker():")
worker_end = content.find("async def handle_natural_language(", worker_start)

if worker_start != -1 and worker_end != -1:
    worker_code = content[worker_start:worker_end]
    
    with open("sara/workers/execution.py", "w") as out:
        out.write('''import asyncio
import os
import aiosqlite
from pathlib import Path
from datetime import datetime
import time
import json
import re

from sara.config.settings import settings
from sara.database.core import get_db, DB_PATH
from sara.core.projects import get_secure_project_dir

AGY_BIN = os.getenv("ANTIGRAVITY_BIN", "agy")

''')
        # We need transition_task, allowed_user_id, bot_app which are in main
        # Wait, moving it blindly might break imports. Let's just keep background_worker in main for a second and integrate execution identity.
