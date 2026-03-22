import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from custom_eval_model import LocalOllamaModel
import os

# Use the same dynamically resolved URL logic for local testing
def get_ollama_url():
    ngrok_url = os.getenv("NGROK_URL", "https://pistillate-quentin-intentioned.ngrok-free.dev")
    mode = os.getenv("OLLAMA_MODE", "ngrok")
    if mode == "ngrok":
        return f"{ngrok_url}/api/generate"
    return "http://localhost:11434/api/generate"

MODEL_NAME = os.getenv("DEFAULT_MODEL", "phi3")
eval_model = LocalOllamaModel(model_name=MODEL_NAME, url=get_ollama_url())

@pytest.mark.parametrize(
    "input_text, actual_output, context",
    [
        (
            "Implement a binary search in Python",
            "Role: Developer\nAction: Binary Search\nContext: Python 3.10\nExplanation: Using iterative approach.",
            ["Binary search is a search algorithm that finds the position of a target value within a sorted array."]
        )
    ]
)
def test_prompt_quality(input_text, actual_output, context):
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        retrieval_context=context
    )
    
    relevancy_metric = AnswerRelevancyMetric(threshold=0.5, model=eval_model)
    hallucination_metric = HallucinationMetric(threshold=0.5, model=eval_model)
    
    assert_test(test_case, [relevancy_metric, hallucination_metric])
