# Open LLM Multi-Agent System

A practical **Planner + Researcher + Executor + Critic** application built in Python with **Ollama**, **FastAPI**, and **DDGS**.

This repo is meant to be know about this project and learning purpose only. You can run it locally, inspect every agent step, and extend it into a more advanced agentic platform later.


## Why this project exists

Most AI demos hide everything inside one giant prompt. That works until the task becomes even slightly messy. The real problem is not generating words. The real problem is building a workflow that can:

- break a goal into steps,
- gather evidence deliberately,
- synthesize a grounded answer,
- and leave behind something you can debug.

That is what this repo does.

## What you get

- **Planner agent** that turns a goal into a structured execution plan.
- **Researcher agent** that runs a no-key web search, fetches selected pages, and turns them into notes.
- **Executor agent** that writes the final answer in an architect-level style.
- **Critic agent** that can trigger one refinement pass.
- **Run store** that saves every execution as JSON under `data/runs/`.
- **FastAPI chat-style UI** for browser testing.
- **CLI** for terminal usage.

## Recommended use case

This is ideal when you want to learn agent orchestration without paying for APIs.

## Repository structure

```text
open-llm-multi-agent-system/
├── app/
│   ├── agents/            # Planner, Researcher, Executor, Critic
│   ├── llm/               # Ollama client wrapper
│   ├── storage/           # JSON run persistence
│   ├── tools/             # Web search + page fetcher
│   ├── api.py             # FastAPI application
│   ├── config.py          # Environment configuration
│   ├── prompts.py         # Agent prompts
│   ├── schemas.py         # Pydantic models
│   └── orchestrator.py    # End-to-end workflow coordinator
├── static/
│   └── index.html         # Lightweight chat-style UI
├── tests/
│   └── ...                # Offline unit tests
├── cli.py
├── Makefile
├── README.md
└── requirements.txt
```

## High-level flow

1. The user sends a goal through the UI or CLI.
2. The **Planner** creates a JSON execution plan.
3. The **Researcher** runs web search for each step and compresses the findings.
4. The **Executor** builds the final answer from the step notes.
5. The **Critic** reviews the draft and optionally triggers one revision.
6. The orchestrator stores everything as a run artifact.

## Prerequisites

- Python **3.11+** recommended
- [Ollama](https://ollama.com/) installed and running
- At least one local model pulled

### Suggested local models

For a first run, stay small and practical.

- `llama3.2:3b` → good default for low-cost local testing
- `qwen2.5:3b` → often better at structured output and analysis
- `mistral` → solid general-purpose alternative if your machine can handle it

## Local quick start

### 1) Install Ollama

Install Ollama from the official site, then confirm it is running.

```bash
ollama
```

### 2) Pull a model

Start with one small model:

```bash
ollama pull llama3.2:3b
```

If you want a stronger executor later, also pull:

```bash
ollama pull qwen2.5:3b
```

### 3) Create a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5) Copy the environment file

```bash
cp .env.example .env
```

The default `.env` is already good enough for a first run.

### 6) Run the CLI

```bash
python cli.py "Design an event-driven architecture for a mid-size SaaS platform, including trade-offs and a phased rollout plan."
```

### 7) Run the web app

```bash
uvicorn app.api:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Example API call

```bash
curl -X POST http://127.0.0.1:8000/api/execute   -H "Content-Type: application/json"   -d '{
    "goal": "Compare service mesh adoption against API gateway only for a platform team with 8 engineers.",
    "context": "Assume limited budget and a preference for open tooling."
  }'
```

## Configuration

Copy `.env.example` to `.env` and adjust only the values you care about.

| Variable | Default | Why it matters |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Where the local model server is reachable |
| `PLANNER_MODEL` | `llama3.2:3b` | Model used for plan generation |
| `RESEARCHER_MODEL` | `llama3.2:3b` | Model used to summarize evidence |
| `EXECUTOR_MODEL` | `llama3.2:3b` | Model used to write the final answer |
| `CRITIC_MODEL` | `llama3.2:3b` | Model used for review |
| `MAX_STEPS` | `4` | Keeps the plan short and practical |
| `MAX_SEARCH_RESULTS` | `5` | Total search results gathered per step |
| `MAX_PAGES_PER_STEP` | `2` | Number of pages from which to fetch content |
| `MAX_EXTRACT_CHARS` | `2200` | Size of page excerpt sent into the model |
| `ENABLE_CRITIC` | `true` | Enables a single review pass |
| `FETCH_URL_CONTENT` | `true` | Toggles page fetching beyond snippets |

## Makefile commands

```bash
make install
make serve
make test
make compile
```


## Troubleshooting

### The app says Ollama is down

- Start Ollama.
- Confirm the API is reachable at `http://localhost:11434`.
- Confirm at least one model is pulled.

### The agent returns weak research notes

- Switch the `RESEARCHER_MODEL` or `EXECUTOR_MODEL` to a stronger local model.
- Increase `MAX_PAGES_PER_STEP` from 2 to 3.
- Lower `MAX_STEPS` so the model spends more effort per step.

### The model returns invalid JSON for planning

- Try `qwen2.5:3b` as the planner.
- Keep the planner model small but instruction-following.

## Where to extend this next

If you want to push this from demo to platform pattern, these are the next upgrades you can make it better :

- add vector memory for long-running projects,
- add role-based tool permissions,
- parallelize independent research steps,
- add citation scoring and reranking,
- replace JSON file storage with PostgreSQL,
- add observability around token counts, latency, and failure reasons.

## License

MIT
