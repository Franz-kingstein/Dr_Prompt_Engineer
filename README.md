# 🩺 Dr. Prompt Engineer: The Professional AI Lifecycle Platform

[![CI/CD Pipeline](https://img.shields.io/badge/CI/CD-GitHub%20Actions-orange)](https://github.com)
[![MLOps](https://img.shields.io/badge/MLOps-Excellent%20Maturity-blue)](https://mlflow.org)
[![Tech Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20Ollama-green)](https://render.com)

**Dr. Prompt Engineer** is a mission-critical platform for the engineering, testing, and monitoring of Large Language Model (LLM) prompts. Unlike basic "chat" apps, this system provides a full production lifecycle—spanning feature store integration, automated quality evaluation, and real-time observability.

## 🌟 Why This Project?
In a world of "black box" AI, Dr. Prompt Engineer brings **transparency** and **governance**. It was built to solve the consistency problem in GenAI by treating prompts as "software assets" that must be versioned, tested, and monitored for quality.

## 🛠️ Technical Architecture
- **Frontend:** React with Vite, styled with a premium "Obsidian" dark design.
- **Backend:** FastAPI (Python) with asynchronous background processing for AI evaluations.
- **LLM Engine:** Multi-mode routing (Ollama local/Ngrok/OpenAI) with self-healing retries.
- **Lifecycle Management:**
    - **Experimentation:** MLflow (SQL-backed) for prompt versioning and tuning.
    - **Feature Serving:** Feast Feature Store for real-time user-context enrichment.
    - **Observability:** Prometheus + Grafana for live quality monitoring.
    - **Evaluation:** DeepEval (Metric-based LLM-as-a-Judge).

## 📊 Quick Links
- **[MLOps Maturity Report](./docs/MLOPS_REPORT.md):** Evidence of the 5/5 MLOps rating.
- **[GenAI Rubric Assessment](./docs/GENAI_RUBRIC.md):** Detailed breakdown of AI logic and prompt engineering methodology.

## ⚙️ Setup & Installation
```bash
# 1. Environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Start Services
prometheus --config.file=prometheus.yml &
sudo systemctl start grafana-server

# 3. Launch
uvicorn main:app --reload
cd frontend && npm run dev
```

---
*Created by [Your Name] for the Karunya Institute of Technology and Sciences.*
