# Runbook

## Local

1. Copy `.env.example` to `.env`
2. Pull Ollama model:
   - `docker compose --profile setup up -d ollama`
   - `docker compose --profile setup run --rm ollama-pull`
3. Build renderer image:
   - `docker compose build renderer-image`
4. Start stack:
   - `docker compose up --build`
5. Run benchmark:
   - `python apps/api/app/tests/e2e/run_benchmark.py`

## Production VM

1. Install Docker + Compose plugin
2. Configure `.env`
3. Start with prod compose:
   - `docker compose -f docker-compose.yml -f infra/compose/compose.prod.yml up -d`
4. Scale workers:
   - `docker compose up -d --scale worker=4`
