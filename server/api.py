"""
FastAPI application exposing the agent via HTTP and serving a simple web UI.

This module creates a global agent instance and defines API endpoints for
chatting with the agent and listing available tools. It also mounts a static
directory containing a minimal HTML/JavaScript client.
"""

from __future__ import annotations

import json
import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import Agent, OllamaBackend

logger = logging.getLogger(__name__)

# Create a FastAPI app
app = FastAPI(title="Local Qwen Agent", version="0.1.0")

# Allow CORS for local development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend and agent. Use the model specified in the environment or default.
MODEL_NAME = "qwen2.5-coder:14b"
backend = OllamaBackend(model=MODEL_NAME)
agent = Agent(backend=backend, tools_config="agent/config/tools.yaml")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message to send to the agent.")
    use_tools: bool = Field(False, description="Whether to allow tool invocations.")


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Chat with the agent. Optionally allow tool use."""
    try:
        reply = agent.chat(req.message, use_tools=req.use_tools)
        return ChatResponse(response=reply)
    except Exception as e:
        logger.exception("Error in chat: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
def list_tools() -> dict:
    """Return a list of available tools."""
    tools_info = []
    for tool in agent.tools.values():
        tools_info.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        })
    return {"tools": tools_info}


@app.get("/")
def root() -> dict:
    """Root endpoint providing a simple greeting and link to web UI."""
    return {
        "message": "Welcome to the Local Qwen Agent API. Access the web UI at /web.",
    }


# Mount the web directory for the front‑end
app.mount("/web", StaticFiles(directory="server/web", html=True), name="web")