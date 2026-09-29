from aiohttp import web
from sara.database.core import get_db
import json

async def handle_index(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SARA Control Plane</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>SARA Control Plane</h1>
        <div class="card">
            <h2>Active Queue</h2>
            <div id="queue">Loading...</div>
        </div>
        <script>
            async function load() {
                const res = await fetch('/api/tasks');
                const tasks = await res.json();
                let html = '';
                for(let t of tasks) {
                    html += `<p><b>#${t.id}</b> ${t.project_name} [${t.status}]<br><i>${t.instruction}</i></p>`;
                }
                document.getElementById('queue').innerHTML = html || 'Queue empty';
            }
            load();
            setInterval(load, 2000);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def handle_api_tasks(request):
    async with await get_db() as db:
        async with db.execute("SELECT id, project_name, status, instruction FROM tasks ORDER BY id DESC LIMIT 20") as cursor:
            tasks = [dict(row) for row in await cursor.fetchall()]
    return web.json_response(tasks)

def setup_web_app():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/tasks', handle_api_tasks)
    return app
