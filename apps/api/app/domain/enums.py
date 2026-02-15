from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    VALIDATING = "validating"
    RENDERING = "rendering"
    RETRYING = "retrying"
    DONE = "done"
    FAILED = "failed"
    TIMEOUT = "timeout"
