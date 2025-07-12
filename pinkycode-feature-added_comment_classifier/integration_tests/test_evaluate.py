import pytest
from unittest.mock import patch
from agent_integration_test_version import evaluate
import json

@pytest.fixture
def mock_response():
    """Fixture to provide a mock response from the model."""
    return {
        "MISSING_COMMENTS": [{"LINE": 5}, {"LINE": 10}],
        "BAD_COMMENTS": [
            {"LINE": 3, "TYPE": "INCORRECT"},
            {"LINE": 7, "TYPE": "USELESS"},
            {"LINE": 15, "TYPE": "VAGUE"},
            {"LINE": 20, "TYPE": "JARGON"},
            {"LINE": 25, "TYPE": "GARBAGE"}
        ],
        "MEANINGLESS_COMMENTS_PERCENTAGE": 40.0
    }

@patch("agent_integration_test_version.client.chat.completions.create")
def test_evaluate_with_comments(mock_create, mock_response, tmp_path):
    """
    Test evaluation of a file with various types of comments.
    """
    # Mock the API response
    mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

    # Create a temporary file with sample code
    code = """
    def add(a, b):  # Adds two numbers
        return a + b

    # This is incorrect
    def subtract(a, b):
        return a - b

    # Redundant comment
    x = 10

    # Vague comment
    y = x * 2

    # Jargon without explanation
    z = y ** 2

    # Nonsensical comment
    print("Hello, World!")
    """
    file_path = tmp_path / "sample_code.py"
    file_path.write_text(code)

    # Call the evaluate function
    result = evaluate(file_path)

    # Assertions
    assert result["filename"] == "sample_code.py"
    assert result["meaningless_pct"] == 40.0
    assert result["issues"]["missing"]["lines"] == [5, 10]
    assert result["issues"]["incorrect"]["lines"] == [3]
    assert result["issues"]["useless"]["lines"] == [7]
    assert result["issues"]["vague"]["lines"] == [15]
    assert result["issues"]["jargon"]["lines"] == [20]
    assert result["issues"]["garbage"]["lines"] == [25]

@patch("agent_integration_test_version.client.chat.completions.create")
def test_evaluate_no_comments(mock_create, tmp_path):
    """
    Test evaluation of a file with no comments.
    """
    # Mock the API response for a file with no comments
    mock_response = {
        "MISSING_COMMENTS": [{"LINE": 3}, {"LINE": 7}],
        "BAD_COMMENTS": [],
        "MEANINGLESS_COMMENTS_PERCENTAGE": 0.0
    }
    mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

    # Create a temporary file with sample code and no comments
    code = """
    def multiply(a, b):
        return a * b

    def divide(a, b):
        return a / b
    """
    file_path = tmp_path / "no_comments.py"
    file_path.write_text(code)

    # Call the evaluate function
    result = evaluate(file_path)

    # Assertions
    assert result["filename"] == "no_comments.py"
    assert result["meaningless_pct"] == 0.0
    assert result["issues"]["missing"]["lines"] == [3, 7]
    assert result["issues"]["incorrect"]["lines"] == []
    assert result["issues"]["useless"]["lines"] == []
    assert result["issues"]["vague"]["lines"] == []
    assert result["issues"]["jargon"]["lines"] == []
    assert result["issues"]["garbage"]["lines"] == []

@patch("agent_integration_test_version.client.chat.completions.create")
def test_evaluate_garbage_comments(mock_create, tmp_path):
    """
    Test evaluation of a file with only garbage comments.
    """
    # Mock the API response for a file with garbage comments
    mock_response = {
        "MISSING_COMMENTS": [],
        "BAD_COMMENTS": [
            {"LINE": 1, "TYPE": "GARBAGE"},
            {"LINE": 2, "TYPE": "GARBAGE"},
            {"LINE": 3, "TYPE": "GARBAGE"}
        ],
        "MEANINGLESS_COMMENTS_PERCENTAGE": 100.0
    }
    mock_create.return_value.choices[0].message.content = json.dumps(mock_response)

    # Create a temporary file with garbage comments
    code = """
    # asdfasdf
    # lkjhgfdsa
    # qwertyuiop
    def dummy():
        pass
    """
    file_path = tmp_path / "garbage_comments.py"
    file_path.write_text(code)

    # Call the evaluate function
    result = evaluate(file_path)

    # Assertions
    assert result["filename"] == "garbage_comments.py"
    assert result["meaningless_pct"] == 100.0
    assert result["issues"]["missing"]["lines"] == []
    assert result["issues"]["incorrect"]["lines"] == []
    assert result["issues"]["useless"]["lines"] == []
    assert result["issues"]["vague"]["lines"] == []
    assert result["issues"]["jargon"]["lines"] == []
    assert result["issues"]["garbage"]["lines"] == [1, 2, 3]