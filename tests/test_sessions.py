import sys
import os
import asyncio
import pytest
import pytest_asyncio
import aiosqlite
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
import main

@pytest_asyncio.fixture
async def setup_test_db():
    original_db_path = main.DB_PATH

    # Create a temporary file for the database
    fd, path = tempfile.mkstemp()
    os.close(fd)

    main.DB_PATH = path

    # Initialize the sessions table
    async with aiosqlite.connect(main.DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                active_project TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notify_enabled INTEGER DEFAULT 1
            )
        ''')
        await db.commit()

    yield path

    # Clean up
    main.DB_PATH = original_db_path
    if os.path.exists(path):
        os.remove(path)

@pytest.mark.asyncio
async def test_get_active_project_none(setup_test_db):
    user_id = 12345
    # Should return None when no project is set
    project = await main.get_active_project(user_id)
    assert project is None

@pytest.mark.asyncio
async def test_set_and_get_active_project(setup_test_db):
    user_id = 12345
    project_name = "test_project"

    # Set the active project
    await main.set_active_project(user_id, project_name)

    # Retrieve it
    project = await main.get_active_project(user_id)
    assert project == project_name

@pytest.mark.asyncio
async def test_update_active_project(setup_test_db):
    user_id = 12345
    initial_project = "first_project"
    new_project = "second_project"

    # Set the initial active project
    await main.set_active_project(user_id, initial_project)
    project = await main.get_active_project(user_id)
    assert project == initial_project

    # Update to a new project
    await main.set_active_project(user_id, new_project)
    project = await main.get_active_project(user_id)
    assert project == new_project

@pytest.mark.asyncio
async def test_multiple_users_active_projects(setup_test_db):
    user_1 = 111
    user_2 = 222

    await main.set_active_project(user_1, "proj_a")
    await main.set_active_project(user_2, "proj_b")

    assert await main.get_active_project(user_1) == "proj_a"
    assert await main.get_active_project(user_2) == "proj_b"
