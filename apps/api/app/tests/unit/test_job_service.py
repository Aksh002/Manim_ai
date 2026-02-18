from app.services.job_service import JobService


def test_job_service_create_and_update() -> None:
    service = JobService()
    job = service.create_job()
    assert job["status"] == "queued"
    assert job["job_id"].startswith("job_")

    updated = service.update_job(job["job_id"], status="rendering", progress=50)
    assert updated is not None
    assert updated["status"] == "rendering"
    assert updated["progress"] == 50
