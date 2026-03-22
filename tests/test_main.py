import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from main import generate_prompt, get_framework, to_json_format

@pytest.mark.asyncio
async def test_get_framework():
    assert get_framework("code") == "RACE"
    assert get_framework("image") == "CARE"
    assert get_framework("document") == "POST"
    assert get_framework("unknown") == "UNKNOWN"

@pytest.mark.asyncio
async def test_generate_prompt_basic():
    prompt = generate_prompt("code", "test task")
    assert "STRICT RACE format" in prompt
    assert "Task: test task" in prompt

@pytest.mark.asyncio
async def test_to_json_format():
    text = "Role: Engineer\nAction: Code"
    result = to_json_format(text)
    assert result == {"Role": "Engineer", "Action": "Code"}

@pytest.mark.asyncio
async def test_validate_output_structure_pass():
    # Mocking structural pass
    from main import validate_output
    output = "Role: x\nAction: y\nContext: z\nExplanation: w"
    
    with patch("main.dynamic_toxicity_check", return_value=(True, "Clean")):
        val, _, _ = await validate_output(output, "RACE")
        assert val["valid"] is True
        assert len(val["issues"]) == 0

@pytest.mark.asyncio
async def test_validate_output_structure_fail():
    from main import validate_output
    output = "Missing headers"
    with patch("main.dynamic_toxicity_check", return_value=(True, "Clean")):
        val, _, _ = await validate_output(output, "RACE")
        assert val["valid"] is False
        assert any("Missing Role:" in issue for issue in val["issues"])

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_dynamic_toxicity_check_pass(mock_post):
    mock_post.return_value = MagicMock()
    mock_post.return_value.json.return_value = {"response": "Toxicity: No\nReason: clear"}
    mock_post.return_value.raise_for_status = MagicMock()
    
    from main import dynamic_toxicity_check
    is_safe, reason = await dynamic_toxicity_check("safe text")
    assert is_safe is True

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_dynamic_toxicity_check_fail(mock_post):
    mock_post.return_value = MagicMock()
    mock_post.return_value.json.return_value = {"response": "Toxicity: Yes\nReason: extreme"}
    mock_post.return_value.raise_for_status = MagicMock()
    
    from main import dynamic_toxicity_check
    is_safe, reason = await dynamic_toxicity_check("bad text")
    assert is_safe is False

@pytest.mark.asyncio
async def test_fast_toxicity_check():
    from main import fast_toxicity_check
    is_safe, reason = fast_toxicity_check("This contains hate speech")
    assert is_safe is False
    assert "Fast-path" in reason

    is_safe, reason = fast_toxicity_check("This is a clean prompt")
    assert is_safe is True

def test_clean_output():
    from main import clean_output
    text = """
Sure, here is your CARE prompt:
**Context:** Sunny day
*Action*: Walking dog
Result : High resolution image
Example: /image sunny_dog
Hope this helps!
"""
    cleaned = clean_output(text, "CARE")
    assert "Context: Sunny day" in cleaned
    assert "Action: Walking dog" in cleaned
    assert "Result: High resolution image" in cleaned
    assert "Example: /image sunny_dog" in cleaned
    assert "Sure, here is your CARE prompt:" not in cleaned
    assert "Hope this helps!" not in cleaned

    text_race = "1. **Role:** Dev\nSome extra line\n- **Action:** Code"
    cleaned_race = clean_output(text_race, "RACE")
    assert "Role: Dev" in cleaned_race
    assert "Action: Code" in cleaned_race
    assert "Some extra line" not in cleaned_race
