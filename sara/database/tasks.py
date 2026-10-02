from sara.database.core import get_db

VALID_TRANSITIONS = {
    'PENDING': ['STARTING', 'CANCELLED'],
    'STARTING': ['RUNNING', 'FAILED', 'CANCELLED', 'INTERRUPTED'],
    'RUNNING': ['SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED'],
    'SUCCESS': [],
    'FAILED': ['PENDING'],
    'TIMEOUT': ['PENDING'],
    'CANCELLED': ['PENDING'],
    'INTERRUPTED': ['PENDING']
}

async def transition_task(task_id: int, new_status: str, pid: int = None, exit_code: int = None, error_msg: str = None):
    async with await get_db() as db:
        async with db.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)) as c:
            row = await c.fetchone()
            if not row: raise ValueError(f"Task {task_id} not found")
            current_status = row['status']
            
        if new_status not in VALID_TRANSITIONS.get(current_status, []) and new_status != 'PENDING':
            raise ValueError(f"Illegal transition: {current_status} -> {new_status}")
                
        updates = ["status = ?"]
        params = [new_status]
        
        if pid is not None:
            updates.append("pid = ?")
            params.append(pid)
        if exit_code is not None:
            updates.append("exit_code = ?")
            params.append(exit_code)
        if error_msg is not None:
            updates.append("error_message = ?")
            params.append(error_msg)
        if new_status == 'STARTING':
            updates.append("started_at = CURRENT_TIMESTAMP")
        if new_status in ['SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED']:
            updates.append("finished_at = CURRENT_TIMESTAMP")
            
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        params.append(task_id)
        
        await db.execute(query, tuple(params))
        await db.commit()

async def get_task(task_id: int):
    async with await get_db() as db:
        async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
            return await cursor.fetchone()
