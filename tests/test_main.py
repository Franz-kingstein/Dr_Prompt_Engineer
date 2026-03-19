import pytest
from unittest.mock import patch, MagicMock
from main import generate_prompt, get_framework, to_json_format, validate_output

def test_get_framework():
    assert get_framework("code") == "RACE"
    assert get_framework("image") == "CARE"
    assert get_framework("document") == "POST"
    assert get_framework("unknown") == "UNKNOWN"

def test_generate_prompt_basic():
    prompt = generate_prompt("code", "test task")
    assert "STRICT RACE format" in prompt
    assert "Task: test task" in prompt

def test_to_json_format():
    text = "Role: Engineer\nAction: Code"
    result = to_json_format(text)
    assert result == {"Role": "Engineer", "Action": "Code"}

def test_validate_output_structure_pass():
    # Mocking structural pass
    output = "Role: x\nAction: y\nContext: z\nExplanation: w"
    
    with patch("main.dynamic_toxicity_check", return_value=(True, "Clean")):
        # We also need to avoid DeepEval during basic structural tests
        # validate_output calls DeepEval metrics if prompt_context is provided
        val = validate_output(output, "RACE")
        assert val["valid"] is True
        assert len(val["issues"]) == 0

def test_validate_output_structure_fail():
    output = "Missing headers"
    with patch("main.dynamic_toxicity_check", return_value=(True, "Clean")):
        val = validate_output(output, "RACE")
        assert val["valid"] is False
        assert any("Missing Role:" in issue for issue in val["issues"])

@patch("main.requests.post")
def test_dynamic_toxicity_check_pass(mock_post):
    mock_post.return_value.json.return_value = {"response": "Toxicity: No\nReason: clear"}
    from main import dynamic_toxicity_check
    is_safe, reason = dynamic_toxicity_check("safe text")
    assert is_safe is True

@patch("main.requests.post")
def test_dynamic_toxicity_check_fail(mock_post):
    mock_post.return_value.json.return_value = {"response": "Toxicity: Yes\nReason: extreme"}
    from main import dynamic_toxicity_check
    is_safe, reason = dynamic_toxicity_check("bad text")
    assert is_safe is False
