import asyncio
from pathlib import Path
from sara.providers.base import AgentProvider
from sara.database.tasks import transition_task

class AntigravityProvider(AgentProvider):
    async def capabilities(self):
        return {
            "supports_background": True,
            "supports_noninteractive": True
        }
        
    async def execute(self, project_path: str, instruction: str, task_id: int, log_file) -> int:
        proj_dir = Path(project_path)
        
        process = await asyncio.create_subprocess_exec(
            "agy", "run", instruction, "--auto-confirm",
            cwd=str(proj_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True
        )
        
        await transition_task(task_id, "RUNNING", pid=process.pid)
        
        async def stream_output(stream, prefix=""):
            async for line in stream:
                decoded = line.decode('utf-8', errors='replace')
                log_file.write(prefix + decoded)
                log_file.flush()
                
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    stream_output(process.stdout),
                    stream_output(process.stderr, prefix="ERR: "),
                    process.wait()
                ),
                timeout=1800
            )
            return process.returncode
        except asyncio.TimeoutError:
            try:
                import os, signal
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except Exception:
                pass
            return 124 # Timeout code
