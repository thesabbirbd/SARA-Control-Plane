import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import get_git_info

# Using tmp_path fixture provided by pytest instead of mocking
def test_get_git_info_no_git_dir(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        # No .git directory

        # Test original implementation fallback or patched implementation
        assert get_git_info("test_project") is None

def test_get_git_info_clean(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("subprocess.check_output") as mock_check_output:
            def side_effect(cmd, **kwargs):
                if "branch" in cmd:
                    return b"main\n"
                elif "status" in cmd:
                    return b""
                elif "log" in cmd:
                    return b"abcdef - Initial commit\n"
                return b""
            mock_check_output.side_effect = side_effect

            result = get_git_info("test_project")
            assert result == {
                "branch": "main",
                "clean": True,
                "commit": "abcdef - Initial commit"
            }

def test_get_git_info_dirty(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("subprocess.check_output") as mock_check_output:
            def side_effect(cmd, **kwargs):
                if "branch" in cmd:
                    return b"main\n"
                elif "status" in cmd:
                    return b" M some_file.py\n"
                elif "log" in cmd:
                    return b"abcdef - Initial commit\n"
                return b""
            mock_check_output.side_effect = side_effect

            result = get_git_info("test_project")
            assert result == {
                "branch": "main",
                "clean": False,
                "commit": "abcdef - Initial commit"
            }

def test_get_git_info_exception(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("subprocess.check_output") as mock_check_output:
            mock_check_output.side_effect = Exception("Git failed")

            assert get_git_info("test_project") is None
