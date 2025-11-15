from __future__ import annotations

import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import Agent, OllamaBackend

logger = logging.getLogger(__name__)

app = FastAPI(title="Local Qwen Agent")

# Restrictive CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-coder:14b")
backend = OllamaBackend(model=MODEL_NAME)
agent = Agent(backend=backend, tools_config="agent/config/tools.yaml")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    use_tools: bool = Field(False, description="Allow tool invocations")

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        reply = agent.chat(req.message, use_tools=req.use_tools)
        return ChatResponse(response=reply)
    except Exception as e:
        logger.exception("Error in /chat: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
def list_tools() -> dict:
    tools_info = []
    for tool in agent.tools.values():
        tools_info.append(
            {"name": tool.name, "description": tool.description, "input_schema": tool.input_schema}
        )
    return {"tools": tools_info}

@app.get("/")
def root() -> dict:
    return {"message": "Local Qwen Agent API. Open /web for UI."}

app.mount("/web", StaticFiles(directory="server/web", html=True), name="web")
