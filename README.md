# 🧬 Production-Ready Self-Improving HyperAgent System

An end-to-end self-improving AI agent framework inspired by **Meta's HyperAgents research**. The system features an autonomous **TaskAgent** operating in a LangGraph ReAct execution loop, a **MetaAgent** that analyzes performance and rewrites prompts and code heuristics across generations, a **Score-Proportional Parent Selection** algorithm, an **LLM Judge Evaluator** with rubric scoring and cost tracking, a **FastAPI backend** with SSE streaming endpoints, a **Streamlit UI** with side-by-side prompt diff viewer, and a **Docker Compose setup with hot-reload**.

---

## 🏛️ System Architecture

```
                  ┌─────────────────────────────────────────┐
                  │          Streamlit Web Interface        │
                  │  (Chat View  |  Evolution Dashboard)    │
                  └────────────────────┬────────────────────┘
                                       │ HTTP / SSE
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │             FastAPI Backend             │
                  │   (/chat/stream, /evolve/trigger, ...)  │
                  └───────┬─────────────────────────┬───────┘
                          │                         │
                          ▼                         ▼
         ┌──────────────────────────┐    ┌──────────────────────────┐
         │   LangGraph TaskAgent    │    │    MetaAgent Mutator     │
         │   (ReAct Loop + Tools)   │    │  (Self-Improvement Loop) │
         └──────────────────────────┘    └────────────┬─────────────┘
                                                      │
                                                      ▼
                                         ┌──────────────────────────┐
                                         │ Score-Proportional Parent│
                                         │ Selection (Softmax/Gen)  │
                                         └────────────┬─────────────┘
                                                      │
                                                      ▼
                                         ┌──────────────────────────┐
                                         │   LLM Judge Evaluator    │
                                         │ (Rubric Score + Costs)   │
                                         └────────────┬─────────────┘
                                                      │
                                                      ▼
                                         ┌──────────────────────────┐
                                         │   Generations Archive    │
                                         │    (JSON Versioning)     │
                                         └──────────────────────────┘
```

---

## 🚀 Key Features

1. **LangGraph ReAct TaskAgent**:
   - Executes domain tasks with built-in tools: Web Search (`web_search`), Calculator (`calculator`), Python REPL (`python_interpreter`), and Data Analyzer (`data_analyzer`).
   - Dynamically loads mutated system prompt directives and code heuristics based on target generation versions ($G_0, G_1, \dots$).

2. **MetaAgent & Self-Improvement Loop**:
   - Autonomously analyzes previous generation execution trajectories and evaluation feedback.
   - Generates mutated system prompts and refined execution heuristics to fix trajectory bottlenecks.

3. **Score-Proportional Parent Selection**:
   - Uses Softmax temperature scaling over rubric evaluation scores:
     $$P(g_i) = \frac{\exp(S(g_i) / \tau)}{\sum_j \exp(S(g_j) / \tau)}$$
   - Selects top-performing parent generations from the archive while preserving evolutionary diversity.

4. **LLM Judge Evaluator & Cost Tracking**:
   - Evaluates TaskAgent executions across benchmark test suites.
   - Structured Rubric Breakdown: **Correctness (40%)**, **Tool Efficiency (30%)**, **Reasoning Clarity (20%)**, **Speed/Cost (10%)**.
   - Calculates prompt/completion token counts and estimated USD costs ($).

5. **FastAPI Streaming Backend**:
   - `/chat/stream`: Server-Sent Events (SSE) endpoint streaming live reasoning steps, tool start/observation events, and typing token output.
   - `/evolve/trigger`: Triggers a 1-click evolutionary cycle with live progress event streams.
   - `/evolution/history` & `/evolution/diff`: Returns line-by-line diffs between parent and mutated child generation prompts.

6. **Streamlit UI Views**:
   - **View 1: Chat View**: Interactive message bubbles, generation version selector, live streaming text reader, and Markdown/JSON chat export buttons.
   - **View 2: Evolution Dashboard View**: Summary KPI metrics, interactive score progression Plotly chart, generation comparison data grid, side-by-side prompt diff viewer, and 'Trigger Evolution' button with real-time log output.

---

## ⚡ Quickstart Guide

### Option 1: Run via Docker Compose (Recommended)
```bash
docker-compose up --build
```
- **Backend FastAPI Docs**: `http://localhost:8000/docs`
- **Streamlit Web UI**: `http://localhost:8501`

### Option 2: Run Locally (Python Virtual Environment)
```bash
# 1. Install Backend Dependencies
pip install -r backend/requirements.txt

# 2. Run Backend FastAPI Server
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload

# 3. In a separate terminal, Run Streamlit Frontend
pip install streamlit plotly pandas
streamlit run frontend/app.py
```

### Option 3: Run Standalone Evaluation Benchmark Script
```bash
python backend/evaluation/run_eval.py
```
This runs a 5-generation self-improvement evaluation loop and generates visual charts in `backend/evaluation/plots/`.

---

## 📊 Evaluation & Visualizations

The evaluation pipeline automatically outputs high-resolution performance plots proving self-improvement:
- `score_progression.png`: Score trajectory curve across generations.
- `rubric_breakdown.png`: Category performance comparison between baseline $G_0$ and evolved generation $G_k$.

---

## 📁 Repository Structure

- `backend/app/hyperagent/`: Core ReAct loop, MetaAgent mutator, selection algorithm, archive manager, evaluator, and tools.
- `backend/app/api/`: FastAPI SSE routers (`chat.py`, `evolve.py`, `evolution.py`).
- `backend/evaluation/`: Benchmark test suite, evaluation pipeline, and plot generator.
- `frontend/views/`: Streamlit Chat view and Evolution Dashboard view.
- `frontend/utils/`: API streaming client and side-by-side diff renderer.
- `docker-compose.yml`: Multi-container orchestrator with hot-reload volume mounts.
