import pytest
import psutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the functions to be tested
from app.utils.helpers import is_process_alive, get_projects, get_git_info, resolve_project_alias

# --- Tests for is_process_alive ---

def test_is_process_alive_none_pid():
    assert is_process_alive(None) is False

@patch('app.utils.helpers.psutil.Process')
def test_is_process_alive_running(mock_process):
    mock_p = MagicMock()
    mock_p.is_running.return_value = True
    mock_p.status.return_value = psutil.STATUS_RUNNING
    mock_process.return_value = mock_p

    assert is_process_alive(1234) is True
    mock_process.assert_called_once_with(1234)

@patch('app.utils.helpers.psutil.Process')
def test_is_process_alive_zombie(mock_process):
    mock_p = MagicMock()
    mock_p.is_running.return_value = True
    mock_p.status.return_value = psutil.STATUS_ZOMBIE
    mock_process.return_value = mock_p

    assert is_process_alive(1234) is False

@patch('app.utils.helpers.psutil.Process')
def test_is_process_alive_not_running(mock_process):
    mock_p = MagicMock()
    mock_p.is_running.return_value = False
    mock_p.status.return_value = psutil.STATUS_STOPPED
    mock_process.return_value = mock_p

    assert is_process_alive(1234) is False

@patch('app.utils.helpers.psutil.Process')
def test_is_process_alive_no_such_process(mock_process):
    mock_process.side_effect = psutil.NoSuchProcess(1234)

    assert is_process_alive(1234) is False

# --- Tests for get_projects ---

@patch('app.utils.helpers.BASE_DIR')
def test_get_projects_no_base_dir(mock_base_dir):
    mock_base_dir.exists.return_value = False
    assert get_projects() == []

@patch('app.utils.helpers.BASE_DIR')
def test_get_projects_with_dirs(mock_base_dir):
    mock_base_dir.exists.return_value = True

    # Create mock paths
    dir1 = MagicMock()
    dir1.is_dir.return_value = True
    dir1.name = "project1"

    dir2 = MagicMock()
    dir2.is_dir.return_value = True
    dir2.name = "project2"

    file1 = MagicMock()
    file1.is_dir.return_value = False
    file1.name = "file.txt"

    hidden_dir = MagicMock()
    hidden_dir.is_dir.return_value = True
    hidden_dir.name = ".hidden_project"

    mock_base_dir.iterdir.return_value = [dir1, dir2, file1, hidden_dir]

    projects = get_projects()
    assert projects == ["project1", "project2"]

# --- Tests for get_git_info ---

@patch('app.utils.helpers.BASE_DIR')
def test_get_git_info_no_git_dir(mock_base_dir):
    mock_proj_dir = MagicMock()
    mock_base_dir.__truediv__.return_value = mock_proj_dir

    mock_git_dir = MagicMock()
    mock_git_dir.exists.return_value = False
    mock_proj_dir.__truediv__.return_value = mock_git_dir

    assert get_git_info("myproject") == ""

@patch('subprocess.check_output')
@patch('app.utils.helpers.BASE_DIR')
def test_get_git_info_clean_repo(mock_base_dir, mock_check_output):
    mock_proj_dir = MagicMock()
    mock_base_dir.__truediv__.return_value = mock_proj_dir

    mock_git_dir = MagicMock()
    mock_git_dir.exists.return_value = True
    mock_proj_dir.__truediv__.return_value = mock_git_dir

    # Mock branch and status outputs
    mock_check_output.side_effect = [
        b"main\n",
        b""
    ]

    assert get_git_info("myproject") == "[main | clean \u2705]"

@patch('subprocess.check_output')
@patch('app.utils.helpers.BASE_DIR')
def test_get_git_info_dirty_repo(mock_base_dir, mock_check_output):
    mock_proj_dir = MagicMock()
    mock_base_dir.__truediv__.return_value = mock_proj_dir

    mock_git_dir = MagicMock()
    mock_git_dir.exists.return_value = True
    mock_proj_dir.__truediv__.return_value = mock_git_dir

    # Mock branch and status outputs
    mock_check_output.side_effect = [
        b"feature-branch\n",
        b" M some_file.py\n"
    ]

    assert get_git_info("myproject") == "[feature-branch | dirty \u26a0\ufe0f]"

@patch('subprocess.check_output')
@patch('app.utils.helpers.BASE_DIR')
def test_get_git_info_exception(mock_base_dir, mock_check_output):
    mock_proj_dir = MagicMock()
    mock_base_dir.__truediv__.return_value = mock_proj_dir

    mock_git_dir = MagicMock()
    mock_git_dir.exists.return_value = True
    mock_proj_dir.__truediv__.return_value = mock_git_dir

    # Mock exception
    mock_check_output.side_effect = Exception("Git error")

    assert get_git_info("myproject") == ""

# --- Tests for resolve_project_alias ---

@patch('app.utils.helpers.get_projects')
def test_resolve_project_alias_exact_match(mock_get_projects):
    mock_get_projects.return_value = ["ProjectA", "ProjectB"]
    assert resolve_project_alias("ProjectA") == "ProjectA"

@patch('app.utils.helpers.get_projects')
def test_resolve_project_alias_case_insensitive_match(mock_get_projects):
    mock_get_projects.return_value = ["ProjectA", "ProjectB"]
    assert resolve_project_alias("projecta") == "ProjectA"
    assert resolve_project_alias("PROJECTB") == "ProjectB"

@patch('app.utils.helpers.get_projects')
def test_resolve_project_alias_no_match(mock_get_projects):
    mock_get_projects.return_value = ["ProjectA", "ProjectB"]
    assert resolve_project_alias("ProjectC") is None
