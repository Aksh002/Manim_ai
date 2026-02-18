from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_render_then_status_flow(monkeypatch) -> None:
    settings = get_settings()
    settings.use_queue = False

    def fake_task(job_id: str, code: str, quality: str, retry_on_error: bool = True) -> None:
        return None

    monkeypatch.setattr("app.api.routes_render.process_render_job", fake_task)

    client = TestClient(app)
    render_payload = {
        "code": "from manim import *\\n\\nclass GeneratedScene(Scene):\\n    def construct(self):\\n        pass\\n",
        "quality": "1080p30",
        "retry_on_error": True,
    }
    response = client.post("/render", json=render_payload)
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    status_response = client.get(f"/status/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "queued"


def test_render_accepts_invalid_code_when_retry_enabled(monkeypatch) -> None:
    settings = get_settings()
    settings.use_queue = False

    def fake_task(job_id: str, code: str, quality: str, retry_on_error: bool = True) -> None:
        return None

    monkeypatch.setattr("app.api.routes_render.process_render_job", fake_task)

    client = TestClient(app)
    invalid_payload = {
        "code": "from manim import *\n\nclass Wrong(Scene):\n    def construct(self):\n        pass\n",
        "quality": "1080p30",
        "retry_on_error": True,
    }
    response = client.post("/render", json=invalid_payload)
    assert response.status_code == 202
