import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import is_process_alive

class TestProcess(unittest.TestCase):
    def test_is_process_alive_falsy_pid(self):
        self.assertFalse(is_process_alive(0))
        self.assertFalse(is_process_alive(None))

    @patch('os.kill')
    def test_is_process_alive_success(self, mock_kill):
        mock_kill.return_value = None
        self.assertTrue(is_process_alive(1234))
        mock_kill.assert_called_once_with(1234, 0)

    @patch('os.kill')
    def test_is_process_alive_oserror(self, mock_kill):
        mock_kill.side_effect = OSError("Mocked OSError")
        self.assertFalse(is_process_alive(1234))
        mock_kill.assert_called_once_with(1234, 0)

if __name__ == "__main__":
    unittest.main()
