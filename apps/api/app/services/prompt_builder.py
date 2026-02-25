from app.schemas.generate import GenerateRequest


def build_generation_prompt(payload: GenerateRequest) -> str:
    return f"""
You are an expert Manim educator creating an educational animation script.

Requirements:
- Return Python code only.
- Must start with: from manim import *
- Must include exactly one Scene class named GeneratedScene inheriting Scene.
- Must define construct(self).
- No unsafe imports, no file/network/system calls.
- Do not invent helper methods on Scene (for example `_set_background`, `_add_area`, `play_and_wait`).
- Only call valid public Manim Scene APIs (for example: play, wait, add, remove, clear, next_section, add_sound).
- Any helper function you use must be explicitly defined in `GeneratedScene`.
- Keep animation approximately {payload.duration_seconds} seconds.
- Audience level: {payload.level.value}
- Style: {payload.style.value}
- Keep code simple and robust for direct rendering in Manim CE.

Topic:
{payload.topic}

Additional instructions:
{payload.additional_instructions or 'None'}

Return only valid Python code.
""".strip()
