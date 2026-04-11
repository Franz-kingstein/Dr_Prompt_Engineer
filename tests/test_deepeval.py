import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from custom_eval_model import LocalOllamaModel
import os

# Use the same dynamically resolved URL logic for local testing
def get_ollama_url():
    ngrok_url = os.getenv("NGROK_URL", "").rstrip("/")
    mode = os.getenv("OLLAMA_MODE", "ngrok").lower()
    
    if mode == "ngrok" and ngrok_url:
        return f"{ngrok_url}/api/generate"
    
    # Fallback/Local
    local_url = os.getenv("LOCAL_OLLAMA_URL", "http://localhost:11434").rstrip("/")
    return f"{local_url}/api/generate"

MODEL_NAME = os.getenv("DEFAULT_MODEL", "phi3")
eval_model = LocalOllamaModel(model_name=MODEL_NAME, url=get_ollama_url())

@pytest.mark.parametrize(
    "input_text, actual_output, context",
    [
        (
            "Implement a binary search in Python",
            "Role: Developer\nAction: Implement a Binary Search using an iterative approach.\nContext: Python 3.10\nExplanation: Iterative approach avoids recursion depth issues.",
            ["The user needs an iterative binary search implemented in Python 3.10 by a Developer."]
        )
    ]
)
def test_prompt_quality(input_text, actual_output, context):
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        context=context,
        retrieval_context=context
    )
    
    relevancy_metric = AnswerRelevancyMetric(threshold=0.5, model=eval_model)
    hallucination_metric = HallucinationMetric(threshold=0.5, model=eval_model)
    
    assert_test(test_case, [relevancy_metric, hallucination_metric])
