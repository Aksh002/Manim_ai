from __future__ import annotations

import hashlib
from threading import Lock

from redis import Redis

from app.core.config import get_settings


class CacheService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._redis: Redis | None = None
        self._mem: dict[str, str] = {}
        self._lock = Lock()
        try:
            self._redis = Redis.from_url(self.settings.redis_url, decode_responses=True)
            self._redis.ping()
        except Exception:
            self._redis = None

    def hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _get(self, key: str) -> str | None:
        if self._redis:
            return self._redis.get(key)
        with self._lock:
            return self._mem.get(key)

    def _set(self, key: str, value: str) -> None:
        if self._redis:
            self._redis.set(key, value)
            return
        with self._lock:
            self._mem[key] = value

    def get_generation(self, request_hash: str) -> str | None:
        return self._get(f"cache:generate:{request_hash}")

    def set_generation(self, request_hash: str, code: str) -> None:
        self._set(f"cache:generate:{request_hash}", code)

    def get_render_job(self, render_hash: str) -> str | None:
        return self._get(f"cache:render:{render_hash}")

    def set_render_job(self, render_hash: str, job_id: str) -> None:
        self._set(f"cache:render:{render_hash}", job_id)
