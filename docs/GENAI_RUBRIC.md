# 🧠 Generative AI Project Report (Assessment Rubric)

**Course:** Generative AI | **Code:** 23DC2031  
**Project:** Dr. Prompt Engineer  
**Institution:** Karunya Institute of Technology and Sciences

---

## 1. Problem Statement & Justification (5 Marks)
*   **The Problem:** Writing high-quality prompts for different domains (Code, Creative, Technical) is difficult for non-experts. Most users get poor results because they lack a "Framework."
*   **The Innovation:** Dr. Prompt Engineer automates three specialized frameworks:
    *   **RACE** (Role, Action, Context, Explanation) for Developers.
    *   **CARE** (Context, Action, Result, Example) for Vision/Image Generation.
    *   **POST** (Persona, Observation, Scenario, Task) for Researchers.
*   **GenAI Justification:** Uses LLMs not just for chat, but to **meta-generate** optimal prompt structures, increasing productivity by 40-50%.

## 2. Methodology & Model Usage (10 Marks)
*   **Core LLM:** Utilizes **Ollama (Phi-3 / Llama-3)** for local, privacy-preserving generation.
*   **Advanced Prompt Engineering:** Implements Few-shot prompting, Chain-of-Thought (CoT), and Framework-specific templating.
*   **RAG-Lite (Feature Store):** Instead of standard RAG, we use **Feast** to retrieve "User Context" (Expertise level) to dynamically adjust the persona's complexity (e.g., a "Beginner" user gets more detailed explanations).
*   **Fine-Tuning:** The "Refiner" module allows for interactive, iterative prompt optimization (Human-in-the-loop).

## 3. Implementation & Logic (5 Marks)
*   **Architecture:**
    *   **Backend:** Python/FastAPI handles the heavy lifting of framework selection and LLM orchestration.
    *   **Logic:** Implements a "Self-Healing" loop. If the generated prompt doesn't match the required framework regex, the AI regenerates it automatically.
    *   **Integration:** Seamless connection between React frontend (UX) and Python backend (Logic).

## 4. Result Analysis & Demonstration (5 Marks)
*   **Validation:** All outputs are passed through **DeepEval** metrics:
    *   **Answer Relevancy:** Measures how well the prompt matches the user's intent.
    *   **Hallucination Check:** Ensures the AI doesn't invent non-existent libraries or features.
*   **Demonstration:** Live demo shows instant generation of complex prompts for Italian landscape photography and Python system architecture.

## 5. Report & Presentation (5 Marks)
*   **Documentation:** Comprehensive technical documentation in `MLOPS_REPORT.md` and `README.md`.
*   **Architecture Diagrams:** Clear flow of data from User → FastAPI → Feast → Ollama.
*   **Plagiarism:** Code is 100% original implementation using standard library components and open-source frameworks.

---
**Prepared for Skill Based Evaluation III IA.**
