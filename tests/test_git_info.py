import sys
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import get_git_info

def test_get_git_info_no_git_dir(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        # Create project dir but no .git dir
        project_dir = tmp_path / "no_git_project"
        project_dir.mkdir()
        assert get_git_info("no_git_project") is None

def test_get_git_info_success(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "good_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("subprocess.check_output") as mock_check_output:
            def mock_subprocess_check_output(args, **kwargs):
                if "branch" in args:
                    return b"main\n"
                elif "status" in args:
                    return b""
                elif "log" in args:
                    return b"abcdef1 - init commit\n"
                return b""

            mock_check_output.side_effect = mock_subprocess_check_output

            result = get_git_info("good_project")
            assert result == {
                "branch": "main",
                "clean": True,
                "commit": "abcdef1 - init commit"
            }

def test_get_git_info_dirty_success(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "dirty_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("subprocess.check_output") as mock_check_output:
            def mock_subprocess_check_output(args, **kwargs):
                if "branch" in args:
                    return b"dev\n"
                elif "status" in args:
                    return b" M some_file.py\n"
                elif "log" in args:
                    return b"1234567 - update\n"
                return b""

            mock_check_output.side_effect = mock_subprocess_check_output

            result = get_git_info("dirty_project")
            assert result == {
                "branch": "dev",
                "clean": False,
                "commit": "1234567 - update"
            }

def test_get_git_info_subprocess_exception(tmp_path):
    with patch("main.BASE_DIR", tmp_path):
        project_dir = tmp_path / "error_project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()

        with patch("subprocess.check_output") as mock_check_output:
            mock_check_output.side_effect = subprocess.CalledProcessError(1, "git")

            result = get_git_info("error_project")
            assert result is None
