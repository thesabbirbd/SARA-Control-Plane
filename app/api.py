from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiosqlite
import os

DB_PATH = os.environ.get("SARA_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "queue.db"))

app = FastAPI(title="SARA Control Plane", version="1.3.100")

@app.get("/api/tasks")
async def get_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, project_name, status, created_at, workflow_id, instruction FROM tasks ORDER BY id DESC LIMIT 50") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@app.get("/api/sessions")
async def get_sessions():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM agent_sessions ORDER BY last_active_at DESC LIMIT 50") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@app.get("/api/stats")
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status") as cursor:
            rows = await cursor.fetchall()
            stats = {row['status']: row['count'] for row in rows}
            return stats

# Serve static files if they exist
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

