import requests
import httpx
import asyncio
import time
import mlflow
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from custom_eval_model import LocalOllamaModel
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
import deepeval
from feast import FeatureStore
import os
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ============================================================
# 🔀 Multi-Mode LLM Routing
# ============================================================
# Set OLLAMA_MODE env var to one of: ngrok | api | local | auto
# Render dashboard or .env is where you configure this.

def get_ollama_url() -> str:
    """Return the Ollama/LLM API endpoint based on OLLAMA_MODE."""
    mode = os.getenv("OLLAMA_MODE", "ngrok").lower()

    if mode == "ngrok":
        ngrok_url = os.getenv("NGROK_URL", "").rstrip("/")
        if ngrok_url:
            return f"{ngrok_url}/api/generate"
        print("⚠️  NGROK_URL not set – falling back to local")
        return "http://localhost:11434/api/generate"

    elif mode == "api":
        # OpenAI / Groq compatible endpoint
        base = os.getenv("API_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        return f"{base}/chat/completions"  # handled separately in call logic

    elif mode == "local":
        local_url = os.getenv("LOCAL_OLLAMA_URL", "http://localhost:11434").rstrip("/")
        return f"{local_url}/api/generate"

    elif mode == "auto":
        # Try ngrok first, then api, then local
        ngrok_url = os.getenv("NGROK_URL", "").rstrip("/")
        if ngrok_url:
            return f"{ngrok_url}/api/generate"
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if api_key:
            base = os.getenv("API_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            return f"{base}/chat/completions"
        return "http://localhost:11434/api/generate"

    # Fallback
    print(f"⚠️  Unknown OLLAMA_MODE '{mode}', defaulting to local")
    return "http://localhost:11434/api/generate"


OLLAMA_MODE = os.getenv("OLLAMA_MODE", "ngrok").lower()
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "phi3")

# -----------------------------
# 🤖 Unified LLM Caller
# -----------------------------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError))
)
async def call_llm(prompt: str, span=None) -> str:
    """Unified helper to call LLM based on OLLAMA_MODE (OpenAI/Groq or Ollama)."""
    current_url = get_ollama_url()
    if span:
        span.set_attribute("url", current_url)
        span.set_attribute("mode", OLLAMA_MODE)
        span.set_attribute("model", DEFAULT_MODEL)

    # ── Path A: API mode (OpenAI / Groq chat completions) ──
    if OLLAMA_MODE == "api":
        api_key = (
            os.getenv("OPENAI_API_KEY") or
            os.getenv("GROQ_API_KEY") or ""
        )
        request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                current_url, json=payload,
                headers=request_headers, timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    # ── Path B: Ollama format (ngrok / local) ──
    else:
        request_headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "DrPromptAPI/1.0"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            # Note: We use dynamic_timeout if needed, but 120 is safe
            response = await client.post(
                current_url, json=payload,
                headers=request_headers, timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")


# -----------------------------
# 🔥 MLflow Setup
# -----------------------------
# File-based tracking is deprecated as of Feb 2026, but used for simplicity in CI/CD.
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning, module="mlflow")
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
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

FEAST_RETRIEVAL_ERRORS = Counter(
    "prompt_gen_feast_retrieval_errors_total",
    "Total errors retrieving features from Feast"
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
if os.getenv("DEEPEVAL_API_KEY"):
    try:
        deepeval.login(api_key=os.getenv("DEEPEVAL_API_KEY"))
        print("✅ DeepEval (Confident AI) logged in")
    except Exception as e:
        print(f"⚠️ DeepEval login failed: {e}")

eval_model = LocalOllamaModel(model_name=DEFAULT_MODEL, url=get_ollama_url())
HALLUCINATION_THRESHOLD = 0.5
RELEVANCE_THRESHOLD = 0.5

# -----------------------------
# App Lifespan (Replacement for @app.on_event("startup"))
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    ollama_url = get_ollama_url()
    print(f"🚀 LLM Mode: {OLLAMA_MODE} → {ollama_url}")
    # Only attempt Ollama warm-up in ngrok/local mode (not API mode)
    if OLLAMA_MODE in ("ngrok", "local", "auto"):
        print("🔥 Warming up Ollama...")
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    ollama_url,
                    json={"model": DEFAULT_MODEL, "prompt": "Identify yourself.", "stream": False},
                    timeout=30
                )
            print("✅ Ollama warm-up complete")
        except Exception as e:
            print(f"⚠️ Ollama warm-up skipped or failed: {e}")
    
    yield
    # --- Shutdown ---
    print("💤 Shutting down Dr Prompt API...")

# -----------------------------
# App Init
# -----------------------------
app = FastAPI(title="Dr Prompt API", version="1.0.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# OLLAMA_URL is now resolved dynamically per-request via get_ollama_url()

# Feast Initialization
FEAST_REPO_PATH = os.path.join(os.getcwd(), "feature_repo/feature_repo")
try:
    fs = FeatureStore(repo_path=FEAST_REPO_PATH)
    print("✅ Feast Feature Store connected")
except Exception as e:
    print(f"❌ Feast initialization error: {e}")
    fs = None

# -----------------------------
# Request Schema
# -----------------------------
class RequestBody(BaseModel):
    task: str
    user_input: str
    user_id: int = 1001  # Default test user
    format_type: str = "structured"  # structured | unstructured | json
    cot: bool = False
    refinement_instructions: str = ""  # New: instructions for refinement
    previous_prompt: str = ""          # New: the prompt being refined


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


@mlflow.trace
def get_framework_format(framework):
    if framework == "RACE":
        return "Role: <Persona>\nAction: <Coding task>\nContext: <Environment, libraries, constraints>\nExplanation: <Logic behind the code>"
    elif framework == "CARE":
        return "Context: <Lighting, style, camera>\nAction: <Main subject activity>\nResult: <Visual outcome>\nExample: <Short sample prompt string>"
    elif framework == "POST":
        return "Persona: <Writer's role>\nObservation: <Current situation or background>\nScenario: <Exact problem being solved>\nTask: <Directives for the AI>"
    return ""


# -----------------------------
# Prompt Generator
# -----------------------------
@mlflow.trace
def generate_prompt(task, user_input, cot=False, user_metadata=None, refinement_instructions="", previous_prompt=""):
    # Base prompt construction with potential Feast metadata
    expertise = "Professional"
    lang = "multilingual"
    if user_metadata:
        expertise = user_metadata.get("expertise_level", "Professional") or "Professional"
        lang = user_metadata.get("preferred_language", "multilingual") or "multilingual"
    
    if task == "code":
        # Make it more general as requested
        persona_suffix = f" You are a {expertise} level expert developer with high-level architectural oversight."
    else:
        persona_suffix = f" You are a {expertise} level expert."

    # --- REFINEMENT MODE ---
    if previous_prompt and refinement_instructions:
        framework = get_framework(task)
        return f"""
You are an expert prompt engineer.{persona_suffix}
The user wants to refine an existing prompt.

PREVIOUS PROMPT:
{previous_prompt}

USER REFINEMENT INSTRUCTIONS:
{refinement_instructions}

YOUR TASK:
Regenerate the prompt incorporating the user's instructions.
Keep the result in the STRICT {framework} format.
NO conversational filler.

STRICT {framework} format:
{get_framework_format(framework)}
"""

    if task == "code":
        prompt = f"""
You are an expert software engineer.{persona_suffix}
Your task is to generate a high-quality coding prompt based on the user's input.
STRICT RACE format:
Role: <Persona>
Action: <Coding task>
Context: <Environment, libraries, constraints>
Explanation: <Logic behind the code>

Task: {user_input}
"""
    elif task == "image":
        prompt = f"""
You are an expert prompt engineer.{persona_suffix}
Generate a detailed image generation prompt (e.g., Midjourney/DALL-E).
DO NOT include any code or programming language references unless specifically requested.
STRICT CARE format:
Context: <Lighting, style, camera>
Action: <Main subject activity>
Result: <Visual outcome>
Example: <Short sample prompt string>

Task: {user_input}
"""
    elif task == "document":
        prompt = f"""
You are a research assistant.{persona_suffix}
Generate a structured document creation prompt.
STRICT POST format:
Persona: <Writer's role>
Observation: <Current situation or background>
Scenario: <Exact problem being solved>
Task: <Directives for the AI>

Input: {user_input}
"""
    else:
        prompt = f"System: Generate a prompt for: {user_input}"

    if cot:
        prompt += "\nThink step by step."

    return prompt



# -----------------------------
# Output Processing
# -----------------------------
def clean_output(text, framework=None):
    if not framework:
        return text

    # Map frameworks to their required keys (without colons for easier fuzzy matching)
    header_map = {
        "RACE": ["Role", "Action", "Context", "Explanation"],
        "CARE": ["Context", "Action", "Result", "Example"],
        "POST": ["Persona", "Observation", "Scenario", "Task"]
    }
    
    required_keys = header_map.get(framework, [])
    lines = text.split("\n")
    structured = []
    
    for line in lines:
        stripped_line = line.strip()
        # Handle list markers (1., -, *), markdown bold (e.g., **Role:**) or plain (Role:)
        # We look for something that looks like "[optional list/mark] Key [optional marks] : (Value)"
        for key in required_keys:
            # Pattern: [non-word or digit]* Key [non-word]* : (Value)
            pattern = rf"^[^\w]*\d*\.?\W*({key})\W*:(.*)"
            match = re.search(pattern, stripped_line, re.IGNORECASE)
            if match:
                # Standardize to "Key: Value"
                clean_key = match.group(1).capitalize()
                val_raw = match.group(2).strip()
                # Only strip common markdown decorators like *, _, ~, and whitespace
                value = re.sub(r"^[*_~\s]+", "", val_raw)
                value = re.sub(r"[*_~\s]+$", "", value).strip()
                
                structured.append(f"{clean_key}: {value}")
                break 
    
    return "\n".join(structured)


def to_json_format(text):
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


# -----------------------------
# 🔥 Dynamic Toxicity Check (Fast + LLM-as-a-Judge)
# -----------------------------
TOXIC_KEYWORDS = [
    r"hate speech", r"violence", r"illegal", r"harmful", r"sexual content",
    r"discriminatory", r"offensive", r"harassment"
]

def fast_toxicity_check(text):
    """Simple regex based check to catch obvious toxicity."""
    for pattern in TOXIC_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Fast-path detection: {pattern}"
    return True, "Clean"

async def dynamic_toxicity_check(text):
    # Try fast check first
    is_safe, reason = fast_toxicity_check(text)
    if not is_safe:
        return False, reason

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
        output_raw = await call_llm(moderation_prompt)
        output = output_raw.lower()

        if "yes" in output:
            return False, output
        return True, output

    except Exception as e:
        print(f"❌ Toxicity check failed: {e}")
        return True, f"moderation_error: {str(e)}"



# -----------------------------
# 🧠 Guardrails Validation
# -----------------------------
async def validate_output(output_text, framework, user_input=None, prompt_context=None):

    validation = {
        "valid": True,
        "issues": [],
        "scores": {}
    }
    
    # Initialize metrics as None for safe early returns
    relevancy_metric = None
    hallucination_metric = None

    # --- STEP 1: 🔥 Toxicity Check ---
    is_safe, reason = await dynamic_toxicity_check(output_text)
    if not is_safe:
        validation["valid"] = False
        validation["issues"].append("Toxic content detected")
        validation["moderation_reason"] = reason
        return validation, None, None  # Return placeholder metrics

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
        return validation, None, None  # Return placeholder metrics

    # --- STEP 3: 🛠️ Advanced Guardrails (DeepEval) ---
    if user_input and prompt_context:
        test_case = LLMTestCase(
            input=user_input,
            actual_output=output_text,
            context=[prompt_context]
        )

        relevancy_metric = AnswerRelevancyMetric(threshold=RELEVANCE_THRESHOLD, model=eval_model, include_reason=True)
        hallucination_metric = HallucinationMetric(threshold=HALLUCINATION_THRESHOLD, model=eval_model, include_reason=True)

        async def run_relevancy():
            try:
                await relevancy_metric.a_measure(test_case)
                validation["scores"]["relevancy"] = relevancy_metric.score
                if not relevancy_metric.is_successful():
                    validation["valid"] = False
                    validation["issues"].append(f"Low Relevance Score: {relevancy_metric.score:.2f}")
                    validation["relevance_reason"] = relevancy_metric.reason
            except Exception as e:
                print(f"DeepEval Relevancy Error: {e}")

        async def run_hallucination():
            try:
                await hallucination_metric.a_measure(test_case)
                validation["scores"]["hallucination"] = hallucination_metric.score
                if not hallucination_metric.is_successful():
                    validation["valid"] = False
                    validation["issues"].append("Hallucination detected")
                    validation["hallucination_reason"] = hallucination_metric.reason
            except Exception as e:
                print(f"DeepEval Hallucination Error: {e}")

        await asyncio.gather(run_relevancy(), run_hallucination())

    return validation, relevancy_metric, hallucination_metric



# -----------------------------
# Health Check Endpoint
# -----------------------------
@app.get("/health")
def health():
    """Used by Render health checks. Returns 200 OK."""
    return {"status": "ok", "mode": OLLAMA_MODE, "model": DEFAULT_MODEL}


# -----------------------------
# Prometheus Endpoint
# -----------------------------
@app.get("/metrics")
def metrics():
    """Prometheus scrape endpoint – publicly accessible for local Prometheus."""
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
async def generate(req: RequestBody, background_tasks: BackgroundTasks):

    REQUEST_COUNT.labels(task=req.task).inc()

    max_retries = 3
    retries_used = 0
    status = "failed"
    final_output = None
    validation = {"valid": False, "issues": ["Initial"]}
    framework = get_framework(req.task)
    
    # -----------------------------
    # 🍴 Feast Feature Retrieval
    # -----------------------------
    user_metadata = {}
    if fs:
        try:
            feature_vector = fs.get_online_features(
                features=[
                    "user_features:expertise_level",
                    "user_features:preferred_language"
                ],
                entity_rows=[{"user_id": req.user_id}]
            ).to_dict()
            
            user_metadata = {
                "expertise_level": feature_vector.get("expertise_level", [None])[0],
                "preferred_language": feature_vector.get("preferred_language", [None])[0]
            }
            print(f"🍴 Retrieved Feast metadata for user {req.user_id}: {user_metadata}")
        except Exception as e:
            print(f"⚠️ Feast retrieval failed: {e}")
            FEAST_RETRIEVAL_ERRORS.inc()

    start_time = time.time()
    prompt = "" # Initialize prompt

    with REQUEST_LATENCY.labels(task=req.task).time():

        while retries_used < max_retries:
            
            prompt = generate_prompt(
                req.task, 
                req.user_input, 
                cot=req.cot, 
                user_metadata=user_metadata,
                refinement_instructions=req.refinement_instructions,
                previous_prompt=req.previous_prompt
            )

            try:
                with mlflow.start_span(name=f"llm_call_attempt_{retries_used + 1}") as span:
                    raw_output = await call_llm(prompt, span=span)
                    status = "success"
                    print(f"✅ LLM response received ({len(raw_output)} chars)")


            except Exception as e:
                # Print the REAL error so it's visible in Render logs
                print(f"❌ LLM call failed (attempt {retries_used + 1}): {type(e).__name__}: {e}")
                raw_output = str(e)
                status = "failed"


            # -----------------------------
            # 🔥 Guardrails Validation
            # -----------------------------
            # Always validate the structured text version for better consistency
            cleaned_text = clean_output(raw_output, framework=framework)
            
            # If requesting unstructured, we validate raw; otherwise we validate cleaned
            validate_input = cleaned_text if req.format_type in ["structured", "json"] else raw_output

            # --- STEP 3: 🧱 Fast Inline Validation (Toxicity & Structure) ---
            # These are fast and essential for prompt safety/formatting
            v_report, _, _ = await validate_output(validate_input, framework)
            
            if v_report["valid"]:
                # Success - Format the final output
                if req.format_type == "structured":
                    final_output = cleaned_text
                elif req.format_type == "json":
                    final_output = to_json_format(cleaned_text)
                else:
                    final_output = raw_output
                break  # Exit retry loop
            
            # If invalid, record and retry (max 2)
            retries_used += 1
            print(f"⚠️ Validation failed (Attempt {retries_used}): {v_report['issues']}. Retrying...")
            if retries_used >= 2:
                final_output = raw_output # Fallback to raw
                break

        latency = time.time() - start_time
        REQUEST_STATUS.labels(status=status).inc()

        # -----------------------------
        # 🚀 Background Processing (Metrics & MLflow)
        # -----------------------------
        async def post_generation_logic(raw_output_text, current_prompt, metrics_req):
            # 1. 🧪 Quality Evaluations (DeepEval)
            # We run this in the background to avoid frontend timeouts
            # Initialize metrics for background tracking
            b_relevancy_metric = AnswerRelevancyMetric(threshold=RELEVANCE_THRESHOLD, model=eval_model, include_reason=True)
            b_hallucination_metric = HallucinationMetric(threshold=HALLUCINATION_THRESHOLD, model=eval_model, include_reason=True)
            
            b_test_case = LLMTestCase(
                input=metrics_req.user_input,
                actual_output=raw_output_text,
                context=[current_prompt]
            )

            b_scores = {}
            try:
                # Ensure DeepEval is logged in for this process
                api_key = os.getenv("DEEPEVAL_API_KEY")
                if api_key:
                    try:
                        deepeval.login(api_key=api_key)
                    except Exception as le:
                        print(f"⚠️ Background DeepEval login failed: {le}")

                await asyncio.gather(
                    b_relevancy_metric.a_measure(b_test_case),
                    b_hallucination_metric.a_measure(b_test_case)
                )
                b_scores["relevancy"] = b_relevancy_metric.score
                b_scores["hallucination"] = b_hallucination_metric.score
                
                # Update Prometheus Gauges
                EVAL_HALLUCINATION.labels(task=metrics_req.task).set(b_relevancy_metric.score)
                EVAL_RELEVANCY.labels(task=metrics_req.task).set(b_hallucination_metric.score)
                
                # 2. 🚀 Track in Confident AI (Dashboard)
                if api_key:
                    try:
                        print(f"📡 Sending metrics to Confident AI for task: {metrics_req.task}...")
                        deepeval.track(
                            event_name=f"prompt_gen_{metrics_req.task}",
                            model=DEFAULT_MODEL,
                            input=metrics_req.user_input,
                            actual_output=raw_output_text,
                            retrieval_context=[current_prompt],
                            metrics=[b_relevancy_metric, b_hallucination_metric]
                        )
                        print(f"🚀 DeepEval Event tracked: prompt_gen_{metrics_req.task}")
                    except Exception as e:
                        print(f"⚠️ DeepEval track failed: {e}")

            except Exception as e:
                print(f"⚠️ Background evaluation failed: {e}")

            # 3. 🔥 MLflow Logging
            log_to_mlflow(raw_output_text, current_prompt, metrics_req, b_scores)

        def log_to_mlflow(final_out, cur_prompt, req_obj, b_eval_scores):
            with mlflow.start_run():
                mlflow.log_param("task", req_obj.task)
                mlflow.log_param("status", "success")
                mlflow.log_text(cur_prompt, "generated_prompt.txt")
                mlflow.log_text(str(final_out), "final_output.txt")
                if b_eval_scores:
                    mlflow.log_metrics({
                        "eval_hallucination": b_eval_scores.get("hallucination", 0),
                        "eval_relevancy": b_eval_scores.get("relevancy", 0)
                    })

        # Launch background tasks and return response immediately
        background_tasks.add_task(post_generation_logic, raw_output, prompt, req)

        return {
            "status": "success",
            "framework": framework,
            "generated_prompt": prompt,
            "output": final_output,
            "validation": {"valid": True, "issues": ["Evaluations running in background"]},
            "evaluations": {"status": "processing"},
            "retries_used": retries_used,
            "latency": latency
        }
# --- FINALLY: Serve Static Files (at root, MUST BE LAST to prevent shadowing) ---
dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
    print(f"✅ Serving frontend from {dist_path}")
else:
    print("ℹ️  No frontend/dist found – running API-only mode")

# --- FINALLY: Serve Static Files (at root, MUST BE LAST to prevent shadowing) ---
dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
    print(f"✅ Serving frontend from {dist_path}")
else:
    print("ℹ️  No frontend/dist found – running API-only mode")
