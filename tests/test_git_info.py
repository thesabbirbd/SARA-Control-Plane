import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import asyncio

import main
from main import get_git_info

class MockProcess:
    def __init__(self, stdout, stderr=b"", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
    
    async def communicate(self):
        return self.stdout, self.stderr

@pytest.mark.asyncio
async def test_get_git_info_no_git_dir(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        assert await get_git_info("test_project") is None

@pytest.mark.asyncio
async def test_get_git_info_clean(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        async def mock_exec(*args, **kwargs):
            if "branch" in args:
                return MockProcess(b"main\n")
            elif "status" in args:
                return MockProcess(b"")
            elif "log" in args:
                return MockProcess(b"abcdef - Initial commit\n")
            return MockProcess(b"")

        with patch("main.asyncio.create_subprocess_exec", side_effect=mock_exec):
            result = await get_git_info("test_project")
            assert result == {
                "branch": "main",
                "clean": True,
                "commit": "abcdef - Initial commit"
            }

@pytest.mark.asyncio
async def test_get_git_info_dirty(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        async def mock_exec(*args, **kwargs):
            if "branch" in args:
                return MockProcess(b"main\n")
            elif "status" in args:
                return MockProcess(b" M some_file.py\n")
            elif "log" in args:
                return MockProcess(b"abcdef - Initial commit\n")
            return MockProcess(b"")

        with patch("main.asyncio.create_subprocess_exec", side_effect=mock_exec):
            result = await get_git_info("test_project")
            assert result == {
                "branch": "main",
                "clean": False,
                "commit": "abcdef - Initial commit"
            }

@pytest.mark.asyncio
async def test_get_git_info_exception(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        async def mock_exec(*args, **kwargs):
            raise Exception("Git failed")

        with patch("main.asyncio.create_subprocess_exec", side_effect=mock_exec):
            # In V1.3.50, when an exception happens in create_subprocess_exec, 
            # get_git_info swallows it and returns default dict.
            result = await get_git_info("test_project")
            assert result is None
