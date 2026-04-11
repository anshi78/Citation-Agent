import os
import time
import traceback
import httpx
from dotenv import load_dotenv
load_dotenv()

import json
from openai import OpenAI
from environment import CitationEnv, Action
from tasks import TASKS

BENCHMARK = "Citation-Agent"

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: list) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def run_inference(task_id):
    # Initialize OpenEnv
    env = CitationEnv(task_id=task_id)
    obs = env.reset()
    
    def _clean(val: str) -> str:
        return val.strip().strip('"').strip("'")

    # Read credentials from environment variables per spec
    # HF_TOKEN has NO default (spec requirement)
    api_key    = os.environ.get("HF_TOKEN")
    base_url   = _clean(os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1"))
    model_name = _clean(os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile"))
    print(f"[DEBUG] base_url={base_url} model={model_name}", flush=True)

    if not api_key:
        print("Warning: HF_TOKEN not provided, returning 0")
        log_start(task=task_id, env=BENCHMARK, model=model_name)
        log_end(success=False, steps=0, score=0.0, rewards=[])
        return 0.0
    api_key = _clean(api_key)

    # Use explicit timeout to avoid hanging connections
    http_client = httpx.Client(timeout=httpx.Timeout(60.0, connect=15.0))
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client
    )
    print(f"[DEBUG] Using base_url={base_url} model={model_name}", flush=True)
    
    system_prompt = """You are an expert Academic Research Assistant. Your goal is to fulfill the task_instruction provided in your observation.
You have SQLite database tools to search for related papers, read abstracts, map citations, and submit paper IDs.

You must output ONLY valid JSON representing your action.
Possible actions:
{"action_type": "search", "query": "exact or partial paper title"}
{"action_type": "read_abstract", "paper_id": "arxiv_id_here"}
{"action_type": "get_citations", "paper_id": "corpus_id_here"}
{"action_type": "submit", "paper_id": "the_found_id_here"}

Do not include any markdown formatting around the JSON (e.g., no ```json ```).
"""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    done = False
    score = 0.0
    steps = 0
    rewards = []
    
    log_start(task=task_id, env=BENCHMARK, model=model_name)
    
    try:
        while not done:
            messages.append({"role": "user", "content": f"Observation: {obs.model_dump_json()}"})
            
            error_msg = None
            action_text = ""
            
            try:
                # Retry on 429 overload OR connection/timeout errors
                max_retries = 4
                last_exc = None
                for attempt in range(max_retries):
                    try:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=messages,
                            temperature=0.0
                        )
                        last_exc = None
                        break  # If successful, exit the retry loop
                    except Exception as api_e:
                        last_exc = api_e
                        err_str = str(api_e)
                        is_429 = '429' in err_str
                        is_conn = any(k in err_str.lower() for k in [
                            'connection', 'timeout', 'connect', 'network',
                            'remotedisconnected', 'connectionreset', 'econnreset'
                        ])
                        if (is_429 or is_conn) and attempt < max_retries - 1:
                            wait = 5 * (attempt + 1)
                            print(f"[DEBUG] Attempt {attempt+1}/{max_retries} failed ({type(api_e).__name__}): {err_str[:200]}. Retrying in {wait}s...", flush=True)
                            time.sleep(wait)
                        else:
                            raise api_e
                if last_exc:
                    raise last_exc
                
                action_text = response.choices[0].message.content.strip()
                # strip markdown formatting if any
                if action_text.startswith("```json"):
                    action_text = action_text[7:-3].strip()
                elif action_text.startswith("```"):
                    action_text = action_text[3:-3].strip()
                    
                action_dict = json.loads(action_text)
                action = Action(**action_dict)
                
                obs, reward, done, info = env.step(action)
                step_reward = reward.value
                
                if done:
                    # Once a submit action completes, final score replaces reward iteration
                    # Clamp to strictly between 0 and 1 (validator requirement)
                    raw_score = float(reward.value)
                    score = max(0.01, min(0.99, raw_score))
                
                rewards.append(step_reward)
                messages.append({"role": "assistant", "content": action_text})
                
                steps += 1
                
                # Single line action for log format compliance
                safe_action_log = action_text.replace('\r', '').replace('\n', ' ')
                log_step(step=steps, action=safe_action_log, reward=step_reward, done=done, error=None)
                
            except Exception as e:
                error_msg = str(e)
                done = True
                rewards.append(0.0)
                steps += 1
                score = 0.01  # Clamp failure score to > 0
                safe_action_log = action_text.replace('\r', '').replace('\n', ' ') if action_text else "None"
                log_step(step=steps, action=safe_action_log, reward=0.0, done=True, error=error_msg)
                print(f"[DEBUG] Error during inference on task {task_id}: {type(e).__name__}: {e}", flush=True)
                print(f"[DEBUG] Full traceback:\n{traceback.format_exc()}", flush=True)
                break
                
        success = (score > 0.5)
        
    finally:
        log_end(success=success, steps=steps, score=score, rewards=rewards)
        
    return score

if __name__ == "__main__":
    scores = {}
    for task in TASKS:
        score = run_inference(task.id)
        scores[task.id] = score
