from celery import Celery
from celery.signals import worker_process_init
from celery.schedules import crontab
import os
import ssl
import logging
logger = logging.getLogger(__name__)

from common.storage_retrieval_services import engine

# Get URLs
BROKER_URL = os.getenv("CELERY_BROKER_URL")
BACKEND_URL = os.getenv("CELERY_RESULTS_BACKEND_URL")

# Log broker and backend URL
logger.info(f"{'Celery Broker URL found' if BROKER_URL else 'Celery Broker URL not found'}")
logger.debug(f"Using Celery Broker: {BROKER_URL}")
logger.info(f"{'Celery Backend URL found' if BROKER_URL else 'Celery Backend URL not found'}")
logger.debug(f"Using Celery Backend: {BACKEND_URL}")

celery_app = Celery(
    "celery_worker",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=[
        "celery_worker.tasks.analyze_application",
        "celery_worker.tasks.generate_survey",
        "celery_worker.tasks.generate_qa_embedding",
        "celery_worker.tasks.generate_store_profile_task",
        "celery_worker.tasks.find_career"
    ],
)

# Configuration
conf = {
    "task_ignore_result": False,
    "task_serializer": "json",
    "accept_content": ["json"],
    "ignore_result": False,
    "timezone": "UTC",
    "enable_utc": True,
    "worker_prefetch_multiplier": 1,
    "broker_connection_retry_on_startup": True,
    "task_acks_late": True,
    "worker_concurrency": os.cpu_count(),
    "task_default_queue": "applications",
    "task_default_exchange": "applications",
    "task_default_routing_key": "applications",
    "task_routes": {"*": {"queue": "applications"}},
}
# Add SSL & timeout/retries to broker for TLS (prod)
if BROKER_URL and BROKER_URL.startswith("amqps://"):
    logger.info("Configuring broker for SSL...")
    conf["broker_use_ssl"] = {
        "cert_reqs": ssl.CERT_NONE,
    }
    conf["broker_connection_timeout"]     = 10
    conf["broker_connection_max_retries"] = 3

# Add SSL to result backend for TLS (prod)
if BACKEND_URL and BACKEND_URL.startswith("rediss://"):
    logger.info("Configuring results backend for SSL...")
    conf["redis_backend_use_ssl"] = {
        "ssl_cert_reqs": ssl.CERT_NONE
    }

# Configure celery
celery_app.conf.update(**conf)

logger.info("Celery worker is configured and ready.")

@worker_process_init.connect
def close_db_connections(**kwargs):
    """
    After forking, drop any inherited DB connections so
    each worker child tests/pings and opens its own fresh socket.
    """
    engine.dispose()

if __name__ == "__main__":
    logger.info("Starting Celery worker...")
    celery_app.start()