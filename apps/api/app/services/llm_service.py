import logging
import re
from typing import Any

import httpx
from openai import BadRequestError, OpenAI

from app.core.config import get_settings
from app.schemas.generate import GenerateRequest
from app.services.prompt_builder import build_generation_prompt

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = self.settings.llm_provider.strip().lower()
        self.openai_client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None
        self.hf_router_client = (
            OpenAI(
                base_url=self.settings.hf_router_base_url.rstrip("/"),
                api_key=self.settings.hf_api_token,
            )
            if self.settings.hf_api_token
            else None
        )
        self.ollama_client = httpx.Client(
            base_url=self.settings.ollama_base_url.rstrip("/"),
            timeout=self.settings.llm_request_timeout_sec,
        )
        self.hf_client = httpx.Client(timeout=self.settings.llm_request_timeout_sec)

    @property
    def model_name(self) -> str:
        if self.provider == "ollama":
            return self.settings.ollama_model
        if self.provider in {"hf_endpoint", "hf_router"}:
            return self.settings.hf_model_id or self.settings.hf_endpoint_url
        return self.settings.openai_model

    def _extract_code(self, text: str) -> str:
        fenced = re.findall(r"```(?:python)?\n([\s\S]*?)```", text)
        if fenced:
            return fenced[0].strip()
        return text.strip()

    def _fallback_code(self, topic: str) -> str:
        safe_topic = topic.replace('"', "'")
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("{safe_topic}", font_size=48)
        self.play(Write(title))
        self.wait(1)
'''

    def _ollama_generate(self, prompt: str, temperature: float | None = None) -> str:
        payload: dict[str, object] = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        }
        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        response = self.ollama_client.post("/api/generate", json=payload)
        if response.is_error:
            detail = response.text.strip()
            raise RuntimeError(f"Ollama error {response.status_code}: {detail}")
        body = response.json()
        text = body.get("response", "")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Ollama returned empty response")
        return text

    def _openai_generate(self, prompt: str, temperature: float | None = None) -> str:
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        payload = {
            "model": self.settings.openai_model,
            "input": prompt,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        try:
            response = self.openai_client.responses.create(**payload)
        except BadRequestError as exc:
            message = str(exc).lower()
            if "temperature" in message and "unsupported" in message and "temperature" in payload:
                payload.pop("temperature", None)
                response = self.openai_client.responses.create(**payload)
            else:
                raise

        return response.output_text

    def _extract_hf_text(self, body: Any, prompt: str) -> str:
        text = ""

        if isinstance(body, list) and body:
            first = body[0]
            if isinstance(first, dict):
                text = str(first.get("generated_text") or first.get("text") or "")

        elif isinstance(body, dict):
            if "error" in body:
                raise RuntimeError(f"HF endpoint error: {body['error']}")

            text = str(body.get("generated_text") or body.get("output_text") or body.get("text") or "")
            if not text and isinstance(body.get("choices"), list) and body["choices"]:
                choice = body["choices"][0]
                if isinstance(choice, dict):
                    message = choice.get("message")
                    if isinstance(message, dict) and isinstance(message.get("content"), str):
                        text = message["content"]
                    elif isinstance(choice.get("text"), str):
                        text = choice["text"]
            if not text and isinstance(body.get("results"), list) and body["results"]:
                first = body["results"][0]
                if isinstance(first, dict):
                    text = str(first.get("generated_text") or first.get("text") or "")

        if text.startswith(prompt):
            text = text[len(prompt) :]
        text = text.strip()
        if not text:
            raise RuntimeError("HF endpoint returned empty response")
        return text

    def _hf_generate(self, prompt: str, temperature: float | None = None) -> str:
        endpoint_url = self.settings.hf_endpoint_url.strip()
        if not endpoint_url:
            raise RuntimeError("HF_ENDPOINT_URL is not configured")

        headers = {"Content-Type": "application/json"}
        if self.settings.hf_api_token:
            headers["Authorization"] = f"Bearer {self.settings.hf_api_token}"

        parameters: dict[str, object] = {
            "max_new_tokens": self.settings.hf_max_new_tokens,
            "return_full_text": False,
        }
        if temperature is not None:
            parameters["temperature"] = temperature

        payload = {
            "inputs": prompt,
            "parameters": parameters,
            "options": {"wait_for_model": True},
        }

        response = self.hf_client.post(endpoint_url, json=payload, headers=headers)
        if response.is_error:
            detail = response.text.strip()
            raise RuntimeError(f"HF endpoint error {response.status_code}: {detail}")
        return self._extract_hf_text(response.json(), prompt)

    def _hf_router_generate(self, prompt: str, temperature: float | None = None) -> str:
        if not self.hf_router_client:
            raise RuntimeError("HF_API_TOKEN is not configured for hf_router provider")

        payload: dict[str, object] = {
            "model": self.settings.hf_model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.settings.hf_max_new_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        completion = self.hf_router_client.chat.completions.create(**payload)
        if not completion.choices:
            raise RuntimeError("HF router returned no choices")

        message = completion.choices[0].message
        content = message.content
        if isinstance(content, list):
            collected: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        collected.append(text)
            content = "\n".join(collected).strip()

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("HF router returned empty message content")
        return content

    def _generate(self, prompt: str, temperature: float | None = None) -> str:
        if self.provider == "ollama":
            return self._ollama_generate(prompt=prompt, temperature=temperature)
        if self.provider == "hf_endpoint":
            return self._hf_generate(prompt=prompt, temperature=temperature)
        if self.provider == "hf_router":
            return self._hf_router_generate(prompt=prompt, temperature=temperature)
        if self.provider == "openai":
            return self._openai_generate(prompt=prompt, temperature=temperature)
        raise RuntimeError(f"Unsupported LLM_PROVIDER: {self.provider}")

    def generate_code(self, payload: GenerateRequest) -> tuple[str, list[str]]:
        prompt = build_generation_prompt(payload)
        try:
            raw = self._generate(prompt=prompt, temperature=0.2)
            return self._extract_code(raw), []
        except Exception as exc:
            logger.warning("Primary LLM generation failed, using fallback template: %s", exc)
            message = str(exc).strip()
            if len(message) > 260:
                message = f"{message[:260]}..."
            return self._fallback_code(payload.topic), [
                f"LLM unavailable ({self.provider}): {message}. Using fallback template"
            ]

    def fix_code(self, code: str, error: str) -> str:
        prompt = f"""
Fix the following Manim script.
Constraints:
- Keep `GeneratedScene(Scene)` and `construct(self)`.
- Use only `from manim import *`.
- No unsafe imports or system/file/network calls.
- Return code only.
- Do not call undefined/private methods on `self` (for example `_set_background`, `_add_area`).
- Do not invent methods like `play_and_wait`; use valid Scene APIs such as `play(...)` and `wait(...)`.
- If you need helper methods, define them explicitly in `GeneratedScene`.
- Ensure final code can render directly with `manim ... GeneratedScene`.

Runtime error:
{error}

Code:
{code}
""".strip()

        try:
            raw = self._generate(prompt=prompt, temperature=0.1)
            return self._extract_code(raw)
        except Exception:
            return code

    def regenerate_with_instruction(self, code: str, instruction: str) -> str:
        prompt = f"""
Revise this Manim script based on the instruction.
Constraints:
- Keep `GeneratedScene(Scene)` and `construct(self)`.
- Use only `from manim import *`.
- No unsafe imports or system/file/network calls.
- Return code only.

Instruction:
{instruction}

Code:
{code}
""".strip()

        try:
            raw = self._generate(prompt=prompt, temperature=0.2)
            return self._extract_code(raw)
        except Exception:
            return code
