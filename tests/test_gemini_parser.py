import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import parse_intent_with_gemini

# Mocks
import main
main.get_projects = lambda: ["test01", "portfolio"]

@pytest.mark.asyncio
async def test_parse_intent_with_gemini_valid_json():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '```json\n{"action": "run_antigravity", "project": "test01", "instruction": "fix the thing"}\n```'}
                    ]
                }
            }
        ]
    }

    with patch('httpx.AsyncClient.post', return_value=mock_response):
        result = await parse_intent_with_gemini("do the thing")
        assert result["action"] == "run_antigravity"
        assert result["project"] == "test01"
        assert result["instruction"] == "fix the thing"
        assert result["task_id"] is None
        assert result["message"] is None

@pytest.mark.asyncio
async def test_parse_intent_with_gemini_malformed_schema():
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Provide a malicious structure where string is expected
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '{"action": "run_antigravity", "project": {"malicious": "dict"}}'}
                    ]
                }
            }
        ]
    }

    with patch('httpx.AsyncClient.post', return_value=mock_response):
        result = await parse_intent_with_gemini("do the thing")
        assert result["action"] == "api_error"
        assert "Invalid schema returned from Gemini" in result["message"]

@pytest.mark.asyncio
async def test_parse_intent_with_gemini_invalid_json():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": 'this is just some text, not json'}
                    ]
                }
            }
        ]
    }

    with patch('httpx.AsyncClient.post', return_value=mock_response):
        result = await parse_intent_with_gemini("do the thing")
        assert result["action"] == "api_error"
        assert "JSONDecodeError" in result["message"] or "Expecting value" in result["message"]
