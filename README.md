---
title: Citation Benchmark
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Citation-Agent — OpenEnv Environment

Citation-Agent is an OpenEnv-compliant environment for training and evaluating agents on academic literature review and citation selection.

Given a claim, the agent must navigate a localized research database to search across papers, read abstracts, traverse citation graphs, and ultimately select the correct paper that supports the claim.

## Motivation

Most agent benchmarks focus on web scraping or terminal navigation. This environment tests an agent's ability to reason over complex scholarly graphs — a real-world task that researchers actually perform daily. The agent must:

- Differentiate between ArXiv IDs and Semantic Scholar Corpus IDs
- Follow citation intents and contexts
- Run SQL-backed queries to find papers in a 891MB database
- Avoid getting stuck in infinite search loops

## Action Space

All actions are JSON objects with an `action_type` field:

| Action | Parameters | Description |
|--------|-----------|-------------|
| `search` | `query: str` | Search papers by title (SQL LIKE). Returns up to 10 results with corpus_id, arxiv_id, title, year. |
| `read_abstract` | `paper_id: str` | Read the abstract of a paper by its arxiv_id. |
| `get_citations` | `paper_id: str` | Get citation context for a paper by its corpus_id. Returns up to 5 citing papers with context, intent, title, abstract. |
| `submit` | `paper_id: str` | Submit the answer. Graded against ground truth. Terminal action. |

## Observation Space

JSON containing:

| Field | Type | Description |
|-------|------|-------------|
| `current_claim` | `str` | The claim/task the agent must resolve |
| `search_results` | `list[dict]` | Results from the last search action |
| `last_abstract` | `str` | Abstract from the last read_abstract action |
| `citations_data` | `list[dict]` | Citation data from the last get_citations action |
| `message` | `str` | Feedback message from the environment |
| `step_count` | `int` | Current step in the episode |

## Reward Function

The reward function provides **dense signal** over the full trajectory:

- **Step penalty**: -0.03 per step (encourages efficiency)
- **Search rewards**: +0.08 to +0.18 for finding relevant papers; -0.12 for no results; -0.22 for repeated no-op searches
- **Read abstract**: +0.06 to +0.12 based on abstract quality; -0.1 for invalid ID
- **Get citations**: +0.06 to +0.15 based on number found; -0.08 for no results
- **Submit correct**: +1.0 plus efficiency bonus (up to +0.2 for solving quickly)
- **Submit wrong**: -0.6 penalty
- **Max steps exceeded**: -1.0

## Tasks (50 total)

Tasks span three difficulty levels with deterministic graders:

| Difficulty | Count | Description | Example |
|------------|-------|-------------|---------|
| **Easy** | ~17 | Direct title search → submit | "Search for paper X. Submit its ID." |
| **Medium** | ~17 | Search + verify metadata → submit | "Find paper X. Verify metadata and return ID." |
| **Hard** | ~16 | Search + check citations → submit | "Search for paper X, check its citations, and submit its ID." |

Each grader checks the submitted `paper_id` against ground truth via exact title match (case-insensitive). Score is binary: 1.0 (correct) or 0.0 (wrong).

## Setup and Usage

### Prerequisites
- Python 3.10+
- Docker (for containerized deployment)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Environment Variables
```bash
export HF_TOKEN="your_huggingface_api_key"
export MODEL_NAME="llama-3.3-70b-versatile"
export API_BASE_URL="https://api.groq.com/openai/v1"
```

### Run Inference (Baseline)
```bash
python inference.py
```

This runs the LLM agent against all 50 tasks, producing structured `[START]`, `[STEP]`, `[END]` logs.

### Run via Docker
```bash
docker build -t citation-agent .
docker run -p 7860:7860 citation-agent
```

The environment server will be accessible at `http://localhost:7860`.

### Deploy to Hugging Face Space
Push to your HF Space repository. The Dockerfile will:
1. Install dependencies
2. Download the 891MB SQLite database from `ruby56/Citation-Database`
3. Start the FastAPI OpenEnv server on port 7860

## Baseline Scores

Using `llama-3.3-70b-versatile` via Groq API:

| Difficulty | Avg Score | Avg Steps |
|------------|-----------|-----------|
| Easy | ~0.8 | ~2-3 |
| Medium | ~0.6 | ~3-5 |
| Hard | ~0.4 | ~5-8 |

## Architecture

- `environment.py`: Core RL environment with actions, transitions, and dense reward logic
- `tasks.py`: 50 tasks with deterministic grader checks
- `server/app.py`: FastAPI OpenEnv server entry point
- `server/citation_environment.py`: OpenEnv-compatible environment wrapper
- `inference.py`: Baseline LLM inference script using OpenAI client
- `openenv.yaml`: OpenEnv manifest
- `Dockerfile`: Container definition for HF Spaces deployment

## Database

The environment uses a 891MB SQLite database (`citation_db.sqlite`) containing:
- `s2_papers`: Semantic Scholar paper metadata (corpus_id, arxiv_id, title, year)
- `arxiv_metadata`: ArXiv paper abstracts
- `citations`: Citation graph with contexts and intents

The database is automatically downloaded from the public HF Dataset [`ruby56/Citation-Database`](https://huggingface.co/datasets/ruby56/Citation-Database) at container build time.
