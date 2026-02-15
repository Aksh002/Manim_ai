from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_job_service
from app.schemas.job import JobStatusResponse
from app.services.job_service import JobService

router = APIRouter(tags=["status"])


@router.get("/status/{job_id}", response_model=JobStatusResponse)
def status(job_id: str, job_service: JobService = Depends(get_job_service)):
    item = job_service.get_job(job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(**item)
