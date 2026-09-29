import sys
import os
import pytest
from unittest.mock import Mock

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from main import authorized, ALLOWED_USER_ID

def test_authorized_user_none():
    """Test when update.effective_user is None."""
    update_mock = Mock()
    update_mock.effective_user = None

    assert authorized(update_mock) == False

def test_authorized_wrong_user():
    """Test when user ID does not match ALLOWED_USER_ID."""
    update_mock = Mock()
    update_mock.effective_user = Mock()
    # Set to a value definitely different from ALLOWED_USER_ID
    update_mock.effective_user.id = ALLOWED_USER_ID + 1

    assert authorized(update_mock) == False

def test_authorized_correct_user():
    """Test when user ID matches ALLOWED_USER_ID."""
    update_mock = Mock()
    update_mock.effective_user = Mock()
    update_mock.effective_user.id = ALLOWED_USER_ID

    assert authorized(update_mock) == True
