from __future__ import annotations

import json
from pathlib import Path

import httpx


def main() -> None:
    prompts_path = Path(__file__).resolve().parents[5] / "docs" / "golden-prompts.json"
    prompts = json.loads(prompts_path.read_text(encoding="utf-8"))

    successes = 0
    with httpx.Client(base_url="http://localhost:8000", timeout=60) as client:
        for prompt in prompts:
            payload = {
                "topic": prompt,
                "duration_seconds": 60,
                "style": "geometric-heavy",
                "level": "school",
                "additional_instructions": "",
            }
            response = client.post("/generate", json=payload)
            if response.status_code == 200 and "GeneratedScene" in response.json().get("code", ""):
                successes += 1

    total = len(prompts)
    print(f"Generation benchmark: {successes}/{total} successful ({(successes / total) * 100:.1f}%)")


if __name__ == "__main__":
    main()
