from fastapi import FastAPI, Response
from pydantic import BaseModel
import requests
import time
import mlflow
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from custom_eval_model import LocalOllamaModel
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

# -----------------------------
# 🔥 MLflow Setup
# -----------------------------
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("Prompt_Generator")

# -----------------------------
# 📊 Prometheus Metrics
# -----------------------------
REQUEST_COUNT = Counter(
    "prompt_gen_requests_total",
    "Total number of prompt generation requests",
    ["task"]
)

REQUEST_LATENCY = Histogram(
    "prompt_gen_latency_seconds",
    "Latency of prompt generation in seconds",
    ["task"]
)

REQUEST_STATUS = Counter(
    "prompt_gen_status_total",
    "Total count of requests by status",
    ["status"]
)

VALIDATION_FAILURES = Counter(
    "prompt_gen_validation_failures_total",
    "Total validation failures",
    ["type"]
)

TOXICITY_DETECTED = Counter(
    "prompt_gen_toxicity_detected_total",
    "Total toxic outputs detected"
)

ADVANACED_GUARDRAIL_FAILURES = Counter(
    "prompt_gen_advanced_guardrail_failures_total",
    "Total failures in advanced guardrails (hallucination/relevance)",
    ["type"]
)

SELF_HEALING_RETRIES = Counter(
    "prompt_gen_self_healing_retries_total",
    "Total self-healing regeneration attempts",
    ["task", "reason"]
)

EVAL_HALLUCINATION = Gauge(
    "prompt_gen_eval_hallucination_score",
    "DeepEval Hallucination score (0-1)",
    ["task"]
)

EVAL_RELEVANCY = Gauge(
    "prompt_gen_eval_relevancy_score",
    "DeepEval Answer Relevancy score (0-1)",
    ["task"]
)

EVAL_CORRECTNESS = Gauge(
    "prompt_gen_eval_correctness_score",
    "DeepEval pseudo-correctness score (0-1)",
    ["task"]
)

# -----------------------------
# DeepEval Init
# -----------------------------
eval_model = LocalOllamaModel(model_name="phi3")
HALLUCINATION_THRESHOLD = 0.5
RELEVANCE_THRESHOLD = 0.5

# -----------------------------
# App Init
# -----------------------------
app = FastAPI()
OLLAMA_URL = "http://localhost:11434/api/generate"

# -----------------------------
# Request Schema
# -----------------------------
class RequestBody(BaseModel):
    task: str
    user_input: str
    format_type: str = "structured"  # structured | unstructured | json
    cot: bool = False


# -----------------------------
# Framework Selector
# -----------------------------
@mlflow.trace
def get_framework(task):
    if task == "code":
        return "RACE"
    elif task == "image":
        return "CARE"
    elif task == "document":
        return "POST"
    return "UNKNOWN"


# -----------------------------
# Prompt Generator
# -----------------------------
@mlflow.trace
def generate_prompt(task, user_input, cot=False):

    if task == "code":
        prompt = f"""
You are an expert software engineer.

Follow STRICT RACE format:
Role:
Action:
Context:
Explanation:

Task: {user_input}
"""

    elif task == "image":
        prompt = f"""
You are an expert prompt engineer.

Follow STRICT CARE format:
Context:
Action:
Result:
Example:

Task: {user_input}
"""

    elif task == "document":
        prompt = f"""
You are a research assistant.

Follow STRICT POST format:
Persona:
Observation:
Scenario:
Task:

Input: {user_input}
"""

    else:
        prompt = user_input

    if cot:
        prompt += "\nThink step by step."

    return prompt


# -----------------------------
# Output Processing
# -----------------------------
def clean_output(text):
    lines = text.split("\n")
    structured = [line for line in lines if ":" in line]
    return "\n".join(structured)


def to_json_format(text):
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


# -----------------------------
# 🔥 Dynamic Toxicity Check (LLM-as-a-Judge)
# -----------------------------
def dynamic_toxicity_check(text):

    moderation_prompt = f"""
You are a strict AI safety moderator.

Analyze the following text and classify it:

Text:
{text}

Return ONLY:
Toxicity: <yes/no>
Reason: <short explanation>
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": moderation_prompt,
                "stream": False
            },
            timeout=60
        )

        result = response.json()
        output = result.get("response", "").lower()

        if "yes" in output:
            return False, output
        return True, output

    except Exception as e:
        return True, f"moderation_error: {str(e)}"


# -----------------------------
# 🧠 Guardrails Validation
# -----------------------------
def validate_output(output_text, framework, user_input=None, prompt_context=None):

    validation = {
        "valid": True,
        "issues": [],
        "scores": {}
    }

    # --- STEP 1: 🔥 Toxicity Check ---
    is_safe, reason = dynamic_toxicity_check(output_text)
    if not is_safe:
        validation["valid"] = False
        validation["issues"].append("Toxic content detected")
        validation["moderation_reason"] = reason
        return validation  # Fail early

    # --- STEP 2: Structure validation ---
    if framework == "RACE":
        required = ["Role:", "Action:", "Context:", "Explanation:"]
    elif framework == "CARE":
        required = ["Context:", "Action:", "Result:", "Example:"]
    elif framework == "POST":
        required = ["Persona:", "Observation:", "Scenario:", "Task:"]
    else:
        required = []

    for field in required:
        if field not in output_text:
            validation["valid"] = False
            validation["issues"].append(f"Missing {field}")
    
    if not validation["valid"]:
        return validation  # Fail early before expensive DeepEval

    # --- STEP 3: 🛠️ Advanced Guardrails (DeepEval) ---
    if user_input and prompt_context:
        test_case = LLMTestCase(
            input=user_input,
            actual_output=output_text,
            context=[prompt_context]
        )

        # Relevancy Check
        relevancy_metric = AnswerRelevancyMetric(threshold=RELEVANCE_THRESHOLD, model=eval_model, include_reason=True)
        try:
            relevancy_metric.measure(test_case)
            validation["scores"]["relevancy"] = relevancy_metric.score
            if not relevancy_metric.is_successful():
                validation["valid"] = False
                validation["issues"].append(f"Low Relevance Score: {relevancy_metric.score:.2f}")
                validation["relevance_reason"] = relevancy_metric.reason
        except Exception as e:
            print(f"DeepEval Relevancy Error: {e}")

        # Hallucination Check
        hallucination_metric = HallucinationMetric(threshold=HALLUCINATION_THRESHOLD, model=eval_model, include_reason=True)
        try:
            hallucination_metric.measure(test_case)
            validation["scores"]["hallucination"] = hallucination_metric.score
            if not hallucination_metric.is_successful():
                validation["valid"] = False
                validation["issues"].append("Hallucination detected")
                validation["hallucination_reason"] = hallucination_metric.reason
        except Exception as e:
            print(f"DeepEval Hallucination Error: {e}")

    return validation



# -----------------------------
# Prometheus Endpoint
# -----------------------------
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# -----------------------------
# Evaluation Runner
# -----------------------------
def run_evaluations(input_text, actual_output, context):
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        context=[context]
    )

    hallucination_metric = HallucinationMetric(threshold=0.5, model=eval_model, include_reason=True)
    relevancy_metric = AnswerRelevancyMetric(threshold=0.5, model=eval_model, include_reason=True)

    scores = {}
    reasons = {}

    try:
        hallucination_metric.measure(test_case)
        scores["hallucination"] = hallucination_metric.score
        reasons["hallucination"] = hallucination_metric.reason
    except Exception as e:
        scores["hallucination"] = 0.0
        reasons["hallucination"] = str(e)

    try:
        relevancy_metric.measure(test_case)
        scores["relevancy"] = relevancy_metric.score
        reasons["relevancy"] = relevancy_metric.reason
    except Exception as e:
        scores["relevancy"] = 0.0
        reasons["relevancy"] = str(e)

    # For "Answer Correctness", DeepEval usually requires an expected_output.
    # We will use relevancy and hallucination to compute a pseudo-correctness 
    # to avoid needing a human ground truth for every generation.
    scores["answer_correctness"] = (1.0 - scores["hallucination"]) * scores["relevancy"]

    return scores, reasons




# -----------------------------
# Main API
# -----------------------------
@app.post("/generate")
@mlflow.trace(name="prompt_gen_pipeline")
def generate(req: RequestBody):

    REQUEST_COUNT.labels(task=req.task).inc()

    max_retries = 3
    retries_used = 0
    status = "failed"
    final_output = None
    validation = {"valid": False, "issues": ["Initial"]}
    framework = get_framework(req.task)
    start_time = time.time()

    with REQUEST_LATENCY.labels(task=req.task).time():

        while retries_used < max_retries:
            
            prompt = generate_prompt(req.task, req.user_input, req.cot)

            try:
                with mlflow.start_span(name=f"ollama_llm_call_attempt_{retries_used + 1}") as span:
                    span.set_attribute("model", "phi3")
                    span.set_attribute("attempt", retries_used + 1)

                    response = requests.post(
                        OLLAMA_URL,
                        json={
                            "model": "phi3",
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=120
                    )

                    response.raise_for_status()
                    result = response.json()
                    raw_output = result.get("response", "")
                    status = "success"
                    span.set_attribute("status", status)

            except Exception as e:
                raw_output = str(e)
                status = "failed"

            # -----------------------------
            # Output Formatting
            # -----------------------------
            if req.format_type == "structured":
                final_output = clean_output(raw_output)
            elif req.format_type == "json":
                final_output = to_json_format(clean_output(raw_output))
            else:
                final_output = raw_output

            # -----------------------------
            # 🔥 Guardrails Validation
            # -----------------------------
            validation = validate_output(
                str(final_output), 
                framework, 
                user_input=req.user_input, 
                prompt_context=prompt
            )

            if validation["valid"]:
                break  # SUCCESS - Exit retry loop
            
            # If invalid, record and retry
            retries_used += 1
            reason = "structure"
            if "Toxic content detected" in validation["issues"]:
                reason = "toxicity"
                TOXICITY_DETECTED.inc()
            elif any("Relevance" in issue for issue in validation["issues"]):
                reason = "relevance"
                ADVANACED_GUARDRAIL_FAILURES.labels(type="relevance").inc()
            elif "Hallucination detected" in validation["issues"]:
                reason = "hallucination"
                ADVANACED_GUARDRAIL_FAILURES.labels(type="hallucination").inc()
            
            SELF_HEALING_RETRIES.labels(task=req.task, reason=reason).inc()
            
            for issue in validation["issues"]:
                VALIDATION_FAILURES.labels(type=issue).inc()

            print(f"⚠️ Validation failed (Attempt {retries_used}): {validation['issues']}. Retrying...")

        latency = time.time() - start_time
        REQUEST_STATUS.labels(status=status).inc()

        # -----------------------------
        # 🧪 DeepEval Scoring (Final results summary)
        # -----------------------------
        eval_scores = validation.get("scores", {})
        eval_reasons = {
            "relevancy": validation.get("relevance_reason", ""),
            "hallucination": validation.get("hallucination_reason", "")
        }

        if status == "success" and validation["valid"]:
            # Record final scores to Prometheus if they exist
            if "hallucination" in eval_scores:
                EVAL_HALLUCINATION.labels(task=req.task).set(eval_scores["hallucination"])
            if "relevancy" in eval_scores:
                EVAL_RELEVANCY.labels(task=req.task).set(eval_scores["relevancy"])
            
            pseudo_correctness = (1.0 - eval_scores.get("hallucination", 0)) * eval_scores.get("relevancy", 0)
            EVAL_CORRECTNESS.labels(task=req.task).set(pseudo_correctness)
            eval_scores["answer_correctness"] = pseudo_correctness


        # -----------------------------
        # 🔥 MLflow Logging
        # -----------------------------
        with mlflow.start_run():
            mlflow.log_param("task", req.task)
            mlflow.log_param("framework", framework)
            mlflow.log_param("format_type", req.format_type)
            mlflow.log_param("status", status)
            mlflow.log_param("validation_passed", validation["valid"])
            mlflow.log_param("retries_used", retries_used)

            mlflow.log_metric("latency", latency)

            mlflow.log_text(prompt, "generated_prompt.txt")
            mlflow.log_text(str(final_output), "final_output.txt")
            mlflow.log_text(str(validation), "validation_report.txt")
            
            if eval_scores:
                mlflow.log_metrics({
                    "eval_hallucination": eval_scores.get("hallucination", 0),
                    "eval_relevancy": eval_scores.get("relevancy", 0),
                    "eval_correctness": eval_scores.get("answer_correctness", 0)
                })
                mlflow.log_text(str(eval_reasons), "evaluation_reasons.txt")

        return {
            "status": status,
            "framework": framework,
            "generated_prompt": prompt,
            "output": final_output,
            "validation": validation,
            "evaluations": eval_scores,
            "retries_used": retries_used,
            "latency": latency
        }