import sys
import os

# Add the app directory to sys.path so we can import from main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

import main
from main import resolve_project_alias

# Mock the get_projects function
def mock_get_projects():
    return ["ProjectA", "test_project", "Another-Project", "xyz123"]

def test_resolve_project_alias(monkeypatch):
    # Use monkeypatch to override the get_projects function in the main module
    monkeypatch.setattr(main, "get_projects", mock_get_projects)

    # 1. Exact match (case insensitive)
    assert resolve_project_alias("projecta") == "ProjectA"
    assert resolve_project_alias("Test_Project") == "test_project"
    assert resolve_project_alias("another-project") == "Another-Project"

    # 2. Partial match (case insensitive)
    assert resolve_project_alias("status for projecta please") == "ProjectA"
    assert resolve_project_alias("update test_project now") == "test_project"
    assert resolve_project_alias("check another-project status") == "Another-Project"

    # 3. Hardcoded aliases
    assert resolve_project_alias("my portfolio is here") == "portfolio"
    assert resolve_project_alias("let's study tonight") == "studyos"
    assert resolve_project_alias("take control now") == "sabbiR-control-plane"

    # 4. No match
    assert resolve_project_alias("this should return nothing") == ""
    assert resolve_project_alias("") == ""
    assert resolve_project_alias("random words") == ""

    # 5. Case handling for hardcoded aliases
    assert resolve_project_alias("PORTFOLIO") == "portfolio"
    assert resolve_project_alias("StUdY") == "studyos"
    assert resolve_project_alias("CoNtRoL") == "sabbiR-control-plane"
