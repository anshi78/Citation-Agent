"""
FastAPI server for the Citation-Agent OpenEnv environment.

Exposes the required OpenEnv endpoints:
  POST /reset   → initialize a new episode
  POST /step    → take an action
  GET  /state   → get current state
  GET  /health  → health check
  GET  /        → root (returns 200)

Usage:
    uvicorn server.app:app --host 0.0.0.0 --port 7860
"""

import os
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Add parent directory to path so we can import environment/tasks
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import CitationEnv, Action, Observation, Reward

app = FastAPI(title="Citation-Agent", description="OpenEnv Citation Agent Environment")

# Global environment instance
_env: Optional[CitationEnv] = None


class ResetRequest(BaseModel):
    task_id: str = "T001"


class StepRequest(BaseModel):
    action_type: str
    query: Optional[str] = None
    paper_id: Optional[str] = None


class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool
    info: dict


@app.get("/")
async def root():
    """Root endpoint — returns 200 for health checks."""
    return {"status": "ok", "environment": "Citation-Agent"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()):
    """Reset the environment for a new episode."""
    global _env
    try:
        _env = CitationEnv(task_id=request.task_id)
        obs = _env.reset()
        return obs.model_dump()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.post("/step")
async def step(request: StepRequest):
    """Take a step in the environment."""
    global _env
    if _env is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )
    try:
        action = Action(
            action_type=request.action_type,
            query=request.query,
            paper_id=request.paper_id,
        )
        obs, reward, done, info = _env.step(action)
        return StepResponse(
            observation=obs.model_dump(),
            reward=reward.value,
            done=done,
            info=info,
        ).model_dump()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.get("/state")
async def state():
    """Get the current environment state."""
    global _env
    if _env is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Environment not initialized. Call /reset first."},
        )
    try:
        obs = _env.state()
        return obs.model_dump()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
