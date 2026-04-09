import os
import asyncio
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from custom_eval_model import LocalOllamaModel

async def showcase():
    print("🧪 Starting DeepEval Showcase...")
    
    # 1. Setup the Judge
    # Using local mode for speed
    model_name = os.getenv("DEFAULT_MODEL", "phi3")
    url = "http://localhost:11434/api/generate"
    eval_model = LocalOllamaModel(model_name=model_name, url=url)
    
    # 2. Define the Test Case
    input_text = "Create a robust Python FastAPI endpoint for user registration."
    actual_output = """
Role: Senior Backend Engineer
Action: Implement a /register POST endpoint using FastAPI and Pydantic.
Context: Python 3.12, SQLAlchemy 2.0, PostgreSQL.
Explanation: The endpoint should validate user input, hash passwords, and handle database persistence.
    """
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        context=["The user wants a clean and production-ready FastAPI registration example."]
    )
    
    # 3. initialize Metric
    metric = AnswerRelevancyMetric(threshold=0.5, model=eval_model, include_reason=True)
    
    # 4. Measure
    print(f"\n📝 Input: {input_text}")
    print(f"🤖 AI Output:\n{actual_output}")
    print("\n⚖️  Judge is evaluating (Answer Relevancy)...")
    
    await metric.a_measure(test_case)
    
    print("\n📊 --- RESULTS ---")
    print(f"✅ Score: {metric.score}")
    print(f"💡 Reason: {metric.reason}")
    print("------------------\n")

if __name__ == "__main__":
    asyncio.run(showcase())
