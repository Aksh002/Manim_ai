# Runbook

## Local

1. Copy `.env.example` to `.env`
2. Configure Hugging Face endpoint in `.env`:
   - `LLM_PROVIDER=hf_router`
   - `HF_ROUTER_BASE_URL=https://router.huggingface.co/v1`
   - `HF_API_TOKEN=<token>`
3. Build renderer image:
   - `docker compose build renderer-image`
4. Start stack:
   - `docker compose up --build`
5. Run benchmark:
   - `python apps/api/app/tests/e2e/run_benchmark.py`

### Optional Ollama mode

- Set `LLM_PROVIDER=ollama`
- Pull model:
  - `docker compose --profile setup up -d ollama`
  - `docker compose --profile setup run --rm ollama-pull`
- `deepseek-coder:6.7b` needs roughly 5.5 GiB free RAM available to Ollama.
- On low-memory machines use `deepseek-coder:1.3b` in `.env`.

## Production VM

1. Install Docker + Compose plugin
2. Configure `.env`
3. Start with prod compose:
   - `docker compose -f docker-compose.yml -f infra/compose/compose.prod.yml up -d`
4. Scale workers:
   - `docker compose up -d --scale worker=4`
