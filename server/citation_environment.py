"""
Citation Environment — OpenEnv-compatible wrapper.

Wraps the core CitationEnv logic into an openenv-core compatible
Environment class that exposes reset(), step(), and state as required
by the OpenEnv FastAPI server.
"""

import sqlite3
import os
from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server.types import (
    Action as BaseAction,
    Observation as BaseObservation,
    State,
)
from openenv.core.env_server.environment import Environment

import tasks


class CitationEnvironment(Environment):
    """
    OpenEnv-compliant citation environment.

    Given a claim, the agent must navigate a localized research database
    to search papers, read abstracts, traverse citation graphs, and
    submit the correct paper ID.
    """

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task = tasks.TASKS[0]
        self._grader = tasks.Grader(self._task)
        self._max_steps = 15
        self._current_obs_data = {}
        self._last_search_query = ""
        self._last_search_signature = ""

        # Database setup
        db_path = "citation_db.sqlite"
        if not os.path.exists(db_path):
            # Also try /app path for Docker containers
            if os.path.exists("/app/citation_db.sqlite"):
                db_path = "/app/citation_db.sqlite"
            else:
                print(f"Database {db_path} not found locally. Downloading from HF Datasets...")
                try:
                    from huggingface_hub import hf_hub_download
                    db_path = hf_hub_download(
                        repo_id="ruby56/Citation-Database",
                        filename="citation_db.sqlite",
                        repo_type="dataset",
                        local_dir=".",
                    )
                    print("Database successfully downloaded!")
                except Exception as e:
                    print(f"WARNING: Could not download DB: {e}")

        self._db = sqlite3.connect(db_path, check_same_thread=False)

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> BaseObservation:
        """Reset the environment for a new episode."""
        # Allow task selection via kwargs
        task_id = kwargs.get("task_id", "T001")
        self._task = next((t for t in tasks.TASKS if t.id == task_id), tasks.TASKS[0])
        self._grader = tasks.Grader(self._task)

        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )
        self._last_search_query = ""
        self._last_search_signature = ""

        self._current_obs_data = {
            "current_claim": self._task.claim,
            "message": "Environment initialized. Search for papers using the SQLite dataset.",
            "search_results": None,
            "last_abstract": None,
            "citations_data": None,
            "step_count": 0,
        }

        return BaseObservation(
            done=False,
            reward=0.0,
            metadata=self._current_obs_data,
        )

    def step(
        self,
        action: BaseAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> BaseObservation:
        """Execute one step in the environment."""
        self._state.step_count += 1
        step_count = self._state.step_count

        # Parse action from metadata
        action_data = {}
        if hasattr(action, "metadata") and action.metadata:
            action_data = action.metadata
        elif hasattr(action, "model_dump"):
            action_data = action.model_dump()

        action_type = action_data.get("action_type", "")
        query = action_data.get("query", "")
        paper_id = action_data.get("paper_id", "")

        reward_value = -0.03
        done = False

        # Max steps guard
        if step_count >= self._max_steps and action_type != "submit":
            self._current_obs_data["message"] = "Max steps reached."
            self._current_obs_data["step_count"] = step_count
            return BaseObservation(
                done=True,
                reward=-1.0,
                metadata=self._current_obs_data,
            )

        cursor = self._db.cursor()
        message = ""

        if action_type == "search":
            q = (query or "").strip()
            if not q:
                message = "Search query is empty."
                reward_value -= 0.15
            else:
                cursor.execute(
                    "SELECT corpus_id, arxiv_id, title, year FROM s2_papers WHERE title LIKE ? LIMIT 10",
                    (f"%{q}%",),
                )
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "corpus_id": str(row[0]),
                        "arxiv_id": str(row[1]),
                        "title": row[2],
                        "year": str(row[3]),
                    })
                self._current_obs_data["search_results"] = results
                message = f"Found {len(results)} papers."

                signature = "|".join((r.get("corpus_id") or "") for r in results)
                repeated_noop = (
                    bool(results)
                    and q.lower() == self._last_search_query
                    and signature == self._last_search_signature
                )

                if results:
                    q_norm = q.lower()
                    best_title = (results[0].get("title") or "").strip().lower()
                    if q_norm and (q_norm == best_title or q_norm in best_title):
                        reward_value += 0.18
                    else:
                        reward_value += 0.08
                    if repeated_noop:
                        reward_value -= 0.22
                        message = f"Found {len(results)} papers. Repeated search detected."
                else:
                    reward_value -= 0.12

                self._last_search_query = q.lower()
                self._last_search_signature = signature

        elif action_type == "read_abstract":
            cursor.execute(
                "SELECT abstract FROM arxiv_metadata WHERE arxiv_id = ?", (paper_id,)
            )
            res = cursor.fetchone()
            if res:
                self._current_obs_data["last_abstract"] = res[0]
                message = f"Abstract for {paper_id} loaded."
                reward_value += 0.12 if res[0] and len(res[0]) > 80 else 0.06
            else:
                message = f"Abstract not found for {paper_id}. Use a valid arxiv_id."
                reward_value -= 0.1

        elif action_type == "get_citations":
            cursor.execute(
                """
                SELECT c.contexts, c.intent, ar.title, ar.abstract
                FROM citations c
                JOIN s2_papers s2_citing ON c.citing_corpus_id = s2_citing.corpus_id
                JOIN arxiv_metadata ar ON s2_citing.arxiv_id = ar.arxiv_id
                WHERE c.cited_corpus_id = ?
                LIMIT 5
                """,
                (paper_id,),
            )
            res = cursor.fetchall()
            if res:
                c_data = []
                for row in res:
                    c_data.append({
                        "contexts": row[0],
                        "intent": row[1],
                        "citing_title": row[2],
                        "citing_abstract": row[3],
                    })
                self._current_obs_data["citations_data"] = c_data
                message = f"Found {len(res)} citations for corpus_id {paper_id}."
                reward_value += min(0.15, 0.06 + (0.01 * len(res)))
            else:
                message = f"No citation data found for corpus_id {paper_id}."
                reward_value -= 0.08

        elif action_type == "submit":
            score = self._grader.score(paper_id or "", self._db)
            if score >= 1.0:
                efficiency_bonus = max(0.0, 0.2 * (1.0 - (step_count / self._max_steps)))
                reward_value = 1.0 + efficiency_bonus
            else:
                reward_value = -0.6
            message = f"Submission graded: {score}"
            done = True

        else:
            message = "Invalid action type."
            reward_value -= 0.2

        self._current_obs_data["message"] = message
        self._current_obs_data["step_count"] = step_count

        return BaseObservation(
            done=done,
            reward=reward_value,
            metadata=self._current_obs_data,
        )

    @property
    def state(self) -> State:
        """Get the current environment state."""
        return self._state
