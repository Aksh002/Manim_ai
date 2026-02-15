from __future__ import annotations

import shutil
from pathlib import Path

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = Path(self.settings.video_storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, job_id: str, src_file: str) -> str:
        target = self.root / f"{job_id}.mp4"
        shutil.copyfile(src_file, target)
        return str(target)

    def clone(self, source_job_id: str, target_job_id: str) -> str | None:
        src = self.root / f"{source_job_id}.mp4"
        if not src.exists():
            return None
        dest = self.root / f"{target_job_id}.mp4"
        shutil.copyfile(src, dest)
        return str(dest)

    def get(self, job_id: str) -> str | None:
        target = self.root / f"{job_id}.mp4"
        return str(target) if target.exists() else None

    def delete(self, job_id: str) -> None:
        target = self.root / f"{job_id}.mp4"
        if target.exists():
            target.unlink()
