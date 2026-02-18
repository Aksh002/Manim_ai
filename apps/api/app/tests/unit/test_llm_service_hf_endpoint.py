from types import SimpleNamespace

from app.services import llm_service


def _fake_settings(**overrides):
    base = {
        "llm_provider": "hf_endpoint",
        "llm_request_timeout_sec": 120,
        "hf_router_base_url": "https://router.huggingface.co/v1",
        "hf_endpoint_url": "https://example.endpoint.aws.endpoints.huggingface.cloud",
        "hf_api_token": "token",
        "hf_model_id": "Qwen/Qwen2.5-Coder-7B-Instruct:nscale",
        "hf_max_new_tokens": 512,
        "openai_api_key": "",
        "openai_model": "gpt-5-mini",
        "ollama_base_url": "http://ollama:11434",
        "ollama_model": "deepseek-coder:1.3b",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_hf_model_name(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "get_settings", lambda: _fake_settings())
    service = llm_service.LLMService()
    assert service.model_name == "Qwen/Qwen2.5-Coder-7B-Instruct:nscale"


def test_extract_hf_text_from_generated_text_list(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "get_settings", lambda: _fake_settings())
    service = llm_service.LLMService()
    text = service._extract_hf_text([{"generated_text": "```python\nprint('x')\n```"}], "ignored")
    assert "print('x')" in text


def test_extract_hf_text_from_choices_schema(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "get_settings", lambda: _fake_settings())
    service = llm_service.LLMService()
    body = {"choices": [{"message": {"content": "```python\nprint('ok')\n```"}}]}
    text = service._extract_hf_text(body, "prompt")
    assert "print('ok')" in text


def test_hf_router_generate_uses_openai_compatible_chat(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "get_settings", lambda: _fake_settings(llm_provider="hf_router"))
    service = llm_service.LLMService()

    class _FakeMessage:
        content = "```python\nprint('router')\n```"

    class _FakeChoice:
        message = _FakeMessage()

    class _FakeCompletions:
        @staticmethod
        def create(**kwargs):
            assert kwargs["model"] == "Qwen/Qwen2.5-Coder-7B-Instruct:nscale"
            assert kwargs["messages"][0]["role"] == "user"
            return SimpleNamespace(choices=[_FakeChoice()])

    service.hf_router_client = SimpleNamespace(chat=SimpleNamespace(completions=_FakeCompletions()))
    text = service._hf_router_generate("generate code", temperature=0.2)
    assert "print('router')" in text
