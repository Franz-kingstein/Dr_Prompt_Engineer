import asyncio
import os
import httpx
import mlflow
import time
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from custom_eval_model import LocalOllamaModel

# --- Configuration ---
MLFLOW_EXPERIMENT = "Prompt_Hyperparameter_Tuning"
# Retrieve URL from env or use local default (matching main.py logic)
OLLAMA_URL = os.getenv("LOCAL_OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate"
MODEL_NAME = os.getenv("DEFAULT_MODEL", "phi3")

# Evaluation Judge (Local Ollama for privacy/speed)
eval_model = LocalOllamaModel(model_name=MODEL_NAME, url=OLLAMA_URL)

async def call_llm_with_temp(prompt: str, temperature: float) -> str:
    """Extension of main.py logic to support variable temperature for tuning."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")

async def run_tuning_experiment():
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    # Test Case Definition
    test_input = "Write a high-performance Python function to calculate Fibonacci numbers using recursion with memoization."
    context = "The user is a professional software engineer looking for clean, documented code."
    
    # Range of temperatures to test
    temperatures = [0.2, 0.5, 0.8]
    
    print(f"🧪 Starting Prompt Tuning Experiment on {MODEL_NAME}...")
    print(f"📝 Test Input: {test_input}")

    for temp in temperatures:
        with mlflow.start_run(run_name=f"temp_{temp}"):
            print(f"\n🔥 Testing Temperature: {temp}")
            
            # 1. Generate Output
            start_time = time.time()
            output = await call_llm_with_temp(test_input, temp)
            latency = time.time() - start_time
            
            # 2. Evaluate with DeepEval
            test_case = LLMTestCase(
                input=test_input,
                actual_output=output,
                context=[context]
            )
            
            relevancy_metric = AnswerRelevancyMetric(threshold=0.5, model=eval_model)
            hallucination_metric = HallucinationMetric(threshold=0.5, model=eval_model)
            
            print("⚖️  Running DeepEval metrics...")
            await asyncio.gather(
                relevancy_metric.a_measure(test_case),
                hallucination_metric.a_measure(test_case)
            )
            
            # 3. Log to MLflow
            mlflow.log_params({
                "model": MODEL_NAME,
                "temperature": temp,
                "task": "code_generation"
            })
            
            mlflow.log_metrics({
                "relevancy_score": relevancy_metric.score,
                "hallucination_score": hallucination_metric.score,
                "latency_seconds": latency
            })
            
            mlflow.log_text(output, "generated_output.txt")
            
            print(f"✅ Results for Temp {temp}: Relevancy={relevancy_metric.score:.2f}, Hallucination={hallucination_metric.score:.2f}")

if __name__ == "__main__":
    asyncio.run(run_tuning_experiment())
    print("\n✨ Hyperparameter Tuning complete. View results in your MLflow Dashboard.")
