from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Manim AI API"
    llm_provider: str = "ollama"
    llm_request_timeout_sec: int = 120

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "deepseek-coder:6.7b"

    redis_url: str = "redis://redis:6379/0"
    use_queue: bool = True

    video_storage_root: str = "/data/videos"
    render_timeout_sec: int = 120
    max_render_retries: int = 2
    render_mode: str = "docker"
    default_render_quality: str = "1080p30"

    renderer_image: str = "manim-ai-renderer:latest"
    sandbox_cpu: str = "1.0"
    sandbox_memory: str = "1g"
    sandbox_pids_limit: int = 256
    sandbox_read_only: bool = True
    sandbox_network_disabled: bool = True
    sandbox_no_new_privileges: bool = True
    sandbox_seccomp_profile: str = "/app/app/sandbox/seccomp/renderer-seccomp.json"

    cors_origins: str = "http://localhost:3000"
    rate_limit_per_min: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
