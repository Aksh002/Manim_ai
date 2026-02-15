import logging
import re

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
        self.ollama_client = httpx.Client(
            base_url=self.settings.ollama_base_url.rstrip("/"),
            timeout=self.settings.llm_request_timeout_sec,
        )

    @property
    def model_name(self) -> str:
        if self.provider == "ollama":
            return self.settings.ollama_model
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
        response.raise_for_status()
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

    def _generate(self, prompt: str, temperature: float | None = None) -> str:
        if self.provider == "ollama":
            return self._ollama_generate(prompt=prompt, temperature=temperature)
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
            return self._fallback_code(payload.topic), [f"LLM unavailable ({self.provider}), using fallback template"]

    def fix_code(self, code: str, error: str) -> str:
        prompt = f"""
Fix the following Manim script.
Constraints:
- Keep `GeneratedScene(Scene)` and `construct(self)`.
- Use only `from manim import *`.
- No unsafe imports or system/file/network calls.
- Return code only.

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
