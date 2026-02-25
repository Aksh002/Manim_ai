# Manim AI Platform

AI-assisted Manim animation generation platform with FastAPI + Next.js + Redis/RQ + sandbox rendering.

## Quick Start

1. Copy env file:
   - `cp .env.example .env`
2. Configure Hugging Face endpoint in `.env`:
   - `LLM_PROVIDER=hf_router`
   - `HF_ROUTER_BASE_URL=https://router.huggingface.co/v1`
   - `HF_API_TOKEN=<your token>`
3. Start stack:
   - `docker compose up --build`
4. Open:
   - Web: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`

Optional (Ollama mode):
- `LLM_PROVIDER=ollama`
- `docker compose --profile setup up -d ollama`
- `docker compose --profile setup run --rm ollama-pull`

## Modes

- Phase 1 style local render (no queue, host manim):
  - `docker compose -f docker-compose.yml -f infra/compose/compose.dev.yml up --build`
- Phase 2 style secure render (queue + sandbox):
  - `docker compose build renderer-image`
  - `docker compose up --build`

## Architecture

- `apps/web`: Next.js frontend
- `apps/api`: FastAPI API + RQ worker
- `containers/renderer`: Sandbox render image for Manim
- `infra`: deployment/runtime configs
- `docs`: architecture and runbooks

## Notes

- Phase 1 includes synchronous local render fallback.
- Phase 2 path (default) uses queue + docker sandbox execution.
- Default LLM provider is Hugging Face Router (`hf_router`, OpenAI-compatible).
- Optional providers: Ollama (`ollama`) and OpenAI (`openai`).
- API contracts are documented in `docs/api-contracts.md`.
- Golden benchmark prompts are in `docs/golden-prompts.json`.
- Benchmark runner: `apps/api/app/tests/e2e/run_benchmark.py`.
