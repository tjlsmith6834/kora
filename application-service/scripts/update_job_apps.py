import logging
import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models_schemas.models import Application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+psycopg2://kora_applications_app:fycjUv-xissiv-kozfu6@52.14.130.173:5432/postgres_db"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

API_BASE = "http://localhost:8002/applications"  # maps to your applications-api container


def run_scan(job_id: str):
    """Scan and process all non-hidden applications for a given job_id."""
    logger.info("Scanning for applications with job_id=%s (ignoring hidden)...", job_id)

    db = SessionLocal()
    try:
        apps = (
            db.query(Application)
            .filter(Application.job_id == job_id)
            .filter(Application.application_status != "hidden")
            .all()
        )

        if not apps:
            logger.info("No active applications found for job_id=%s", job_id)
            return

        logger.info("Found %d applications to process for job_id=%s", len(apps), job_id)

        for app in apps:
            url = f"{API_BASE}/{app.application_id}/new_profile/"
            logger.info("POST %s", url)
            try:
                r = requests.post(url)
                if r.status_code == 200:
                    logger.info("✅ Queued via API: %s", r.json())
                else:
                    logger.error("❌ Failed to queue %s: %s", app.application_id, r.text)
            except Exception as e:
                logger.error("❌ Exception posting %s: %s", app.application_id, e)

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scan_by_job.py <job_id>")
        sys.exit(1)

    job_id_arg = sys.argv[1]
    run_scan(job_id_arg)