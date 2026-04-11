import sqlite3
import os
from typing import Optional, List, Dict, Any, Union, Tuple
from pydantic import BaseModel, Field
import tasks

class Observation(BaseModel):
    current_claim: str
    search_results: Optional[List[Dict[str, str]]] = None
    last_abstract: Optional[str] = None
    citations_data: Optional[List[Dict[str, str]]] = None
    message: Optional[str] = None
    step_count: int = 0

class Action(BaseModel):
    action_type: str = Field(..., description="One of: 'search', 'read_abstract', 'get_citations', 'submit'")
    query: Optional[str] = Field(None, description="Search term (used only for 'search')")
    paper_id: Optional[str] = Field(None, description="Paper ID (corpus_id or arxiv_id) to read or submit")

class Reward(BaseModel):
    value: float
    is_terminal: bool
    details: str

class CitationEnv:
    def __init__(self, task_id: str = "T001"):
        self.task = next((t for t in tasks.TASKS if t.id == task_id), tasks.TASKS[0])
        self.grader = tasks.Grader(self.task)
        self.step_count = 0
        self.max_steps = 15
        self.state_history = []
        self._current_obs = None
        self._last_search_query = ""
        self._last_search_signature = ""
        
        db_path = 'citation_db.sqlite'
        if not os.path.exists(db_path):
            # Also try /app path for Docker containers
            if os.path.exists("/app/citation_db.sqlite"):
                db_path = "/app/citation_db.sqlite"
            else:
                print(f"Database {db_path} not found locally. Downloading from HF Datasets...")
                try:
                    from huggingface_hub import hf_hub_download
                    # Pulls directly from the Dataset instead of the Space
                    db_path = hf_hub_download(repo_id="ruby56/Citation-Database", filename="citation_db.sqlite", repo_type="dataset", local_dir=".")
                    print("Database successfully mounted!")
                except Exception as e:
                    print(f"WARNING: Could not download DB: {e}")
                
        self.db = sqlite3.connect(db_path)
        
    def reset(self) -> Observation:
        self.step_count = 0
        self.state_history = []
        self._last_search_query = ""
        self._last_search_signature = ""
        self._current_obs = Observation(
            current_claim=self.task.claim,
            message="Environment initialized. Please search for papers using the SQLite dataset."
        )
        self.state_history.append(self._current_obs)
        return self._current_obs

    def state(self) -> Observation:
        if not self._current_obs:
            return self.reset()
        return self._current_obs

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, dict]:
        self.step_count += 1
        done = False
        info = {"task": self.task.id}
        
        # Small step penalty encourages shorter trajectories.
        reward_value = -0.03
        reward_details = "Step taken."

        if self.step_count >= self.max_steps and action.action_type != "submit":
            return self._current_obs, Reward(value=-1.0, is_terminal=True, details="Max steps reached."), True, info
        
        message = ""
        search_results = self._current_obs.search_results if self._current_obs else None
        last_abstract = self._current_obs.last_abstract if self._current_obs else None
        citations_data = self._current_obs.citations_data if self._current_obs else None

        cursor = self.db.cursor()

        if action.action_type == "search":
            q = (action.query or "")
            if not q.strip():
                message = "Search query is empty."
                reward_value -= 0.15
                new_obs = Observation(
                    current_claim=self.task.claim,
                    search_results=search_results,
                    last_abstract=last_abstract,
                    citations_data=citations_data,
                    message=message,
                    step_count=self.step_count,
                )
                self._current_obs = new_obs
                self.state_history.append(new_obs)
                info["history_len"] = len(self.state_history)
                return new_obs, Reward(value=reward_value, is_terminal=False, details=reward_details), False, info

            query = "SELECT corpus_id, arxiv_id, title, year FROM s2_papers WHERE title LIKE ? LIMIT 10"
            cursor.execute(query, (f"%{q}%",))
            results = []
            for row in cursor.fetchall():
                results.append({"corpus_id": str(row[0]), "arxiv_id": str(row[1]), "title": row[2], "year": str(row[3])})
            search_results = results
            message = f"Found {len(results)} papers."

            signature = "|".join((r.get("corpus_id") or "") for r in results)
            repeated_noop = (
                bool(results)
                and q.strip().lower() == self._last_search_query
                and signature == self._last_search_signature
            )

            if results:
                q_norm = q.strip().lower()
                best_title = (results[0].get("title") or "").strip().lower()
                if q_norm and (q_norm == best_title or q_norm in best_title):
                    reward_value += 0.18
                else:
                    reward_value += 0.08

                # Discourage repeated searches that do not add new information.
                if repeated_noop:
                    reward_value -= 0.22
                    message = f"Found {len(results)} papers. Repeated no-op search detected."
            else:
                reward_value -= 0.12

            self._last_search_query = q.strip().lower()
            self._last_search_signature = signature
            
        elif action.action_type == "read_abstract":
            pid = action.paper_id
            cursor.execute("SELECT abstract FROM arxiv_metadata WHERE arxiv_id = ?", (pid,))
            res = cursor.fetchone()
            if res:
                last_abstract = res[0]
                message = f"Abstract for {pid} loaded."
                reward_value += 0.12 if last_abstract and len(last_abstract) > 80 else 0.06
            else:
                message = f"Abstract not found for {pid}. Make sure to pass a valid arxiv_id."
                reward_value -= 0.1
                
        elif action.action_type == "get_citations":
            pid = action.paper_id
            query = """
                SELECT c.contexts, c.intent, ar.title, ar.abstract
                FROM citations c
                JOIN s2_papers s2_citing ON c.citing_corpus_id = s2_citing.corpus_id
                JOIN arxiv_metadata ar ON s2_citing.arxiv_id = ar.arxiv_id
                WHERE c.cited_corpus_id = ?
                LIMIT 5
            """
            cursor.execute(query, (pid,))
            res = cursor.fetchall()
            if res:
                c_data = []
                for row in res:
                    c_data.append({"contexts": row[0], "intent": row[1], "citing_title": row[2], "citing_abstract": row[3]})
                citations_data = c_data
                message = f"Found {len(res)} valid citations with abstracts for corpus_id {pid}."
                reward_value += min(0.15, 0.06 + (0.01 * len(res)))
            else:
                message = f"No citation graph data found for corpus_id {pid}."
                reward_value -= 0.08
                
        elif action.action_type == "submit":
            pid = action.paper_id or ""
            score = self.grader.score(pid, self.db)
            # Strongly penalize wrong terminal submissions and reward correct early solves.
            if score >= 1.0:
                efficiency_bonus = max(0.0, 0.2 * (1.0 - (self.step_count / self.max_steps)))
                reward_value = 1.0 + efficiency_bonus
            else:
                reward_value = -0.6
            reward_details = f"Final submission scored {score}"
            message = f"Submission graded: {score}"
            done = True
            
        else:
            message = "Invalid action."
            reward_value -= 0.2

        new_obs = Observation(
            current_claim=self.task.claim,
            search_results=search_results,
            last_abstract=last_abstract,
            citations_data=citations_data,
            message=message,
            step_count=self.step_count
        )
        self._current_obs = new_obs
        self.state_history.append(new_obs)
        info["history_len"] = len(self.state_history)

        return new_obs, Reward(value=reward_value, is_terminal=done, details=reward_details), done, info
