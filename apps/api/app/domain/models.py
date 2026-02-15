from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.enums import JobStatus


@dataclass
class JobRecord:
    job_id: str
    status: JobStatus
    progress: int = 0
    stage: str = "queued"
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    video_path: Optional[str] = None
