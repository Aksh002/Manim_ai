import logging

from redis import Redis
from rq import Worker

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def run_worker() -> None:
    settings = get_settings()
    redis_conn = Redis.from_url(settings.redis_url)
    worker = Worker(["render"], connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    run_worker()
