from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.api.deps import get_cache_service, get_job_service, get_queue, get_storage_service
from app.core.config import get_settings
from app.domain.enums import JobStatus
from app.schemas.render import RenderRequest, RenderResponse
from app.services.cache_service import CacheService
from app.services.code_validator import CodeValidator
from app.services.job_service import JobService
from app.services.storage_service import StorageService
from app.workers.tasks_render import process_render_job

router = APIRouter(tags=["render"])
validator = CodeValidator()


@router.post("/render", response_model=RenderResponse, status_code=status.HTTP_202_ACCEPTED)
def render(
    payload: RenderRequest,
    background_tasks: BackgroundTasks,
    job_service: JobService = Depends(get_job_service),
    storage_service: StorageService = Depends(get_storage_service),
    cache_service: CacheService = Depends(get_cache_service),
):
    validation = validator.validate(payload.code)
    if not validation.ok and not payload.retry_on_error:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})

    render_hash = cache_service.hash_text(f"render:v2:{payload.quality}:{payload.code}")
    cached_job_id = cache_service.get_render_job(render_hash)
    if cached_job_id:
        cached_video = storage_service.get(cached_job_id)
        if cached_video:
            record = job_service.create_job()
            cloned = storage_service.clone(cached_job_id, record["job_id"])
            if cloned:
                job_service.update_job(
                    record["job_id"],
                    status=JobStatus.DONE.value,
                    stage="done",
                    progress=100,
                    video_path=cloned,
                )
                return RenderResponse(job_id=record["job_id"], status=JobStatus.DONE.value)

    record = job_service.create_job()
    settings = get_settings()

    if settings.use_queue:
        queue = get_queue()
        queue.enqueue(
            "app.workers.tasks_render.process_render_job",
            record["job_id"],
            payload.code,
            payload.quality,
            payload.retry_on_error,
            job_timeout=settings.render_timeout_sec + 20,
        )
    else:
        background_tasks.add_task(
            process_render_job,
            record["job_id"],
            payload.code,
            payload.quality,
            payload.retry_on_error,
        )

    cache_service.set_render_job(render_hash, record["job_id"])
    return RenderResponse(job_id=record["job_id"], status=record["status"])
