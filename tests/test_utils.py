import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import is_process_alive

def test_is_process_alive_no_pid():
    assert is_process_alive(None) is False
    assert is_process_alive(0) is False

@patch('os.kill')
def test_is_process_alive_true(mock_kill):
    # Mocking os.kill to not raise an exception
    mock_kill.return_value = None
    assert is_process_alive(1234) is True
    mock_kill.assert_called_once_with(1234, 0)

@patch('os.kill')
def test_is_process_alive_false_oserror(mock_kill):
    # Mocking os.kill to raise OSError (e.g. Process doesn't exist)
    mock_kill.side_effect = OSError("No such process")
    assert is_process_alive(9999) is False
    mock_kill.assert_called_once_with(9999, 0)
