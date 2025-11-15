"""
Integration tests for the FastAPI server.

These tests override the agent's backend to avoid calling a real model.
"""

import json

from fastapi.testclient import TestClient

import server.api as api


class DummyBackend:
    def generate(self, prompt, history, system_prompt=None, model=None):
        return "dummy response"


def test_chat_endpoint(monkeypatch):
    # Override backend and agent backend with dummy
    dummy = DummyBackend()
    monkeypatch.setattr(api, "backend", dummy)
    monkeypatch.setattr(api, "agent", api.Agent(backend=dummy, tools_config="agent/config/tools.yaml"))

    client = TestClient(api.app)
    resp = client.post("/chat", json={"message": "hello", "use_tools": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"] == "dummy response"


def test_tools_endpoint(monkeypatch):
    dummy = DummyBackend()
    monkeypatch.setattr(api, "backend", dummy)
    monkeypatch.setattr(api, "agent", api.Agent(backend=dummy, tools_config="agent/config/tools.yaml"))
    client = TestClient(api.app)
    resp = client.get("/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("tools"), list)