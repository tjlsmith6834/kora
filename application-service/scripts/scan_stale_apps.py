import logging
from datetime import datetime, timedelta
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

def run_scan():
    cutoff = datetime.utcnow() - timedelta(hours=2)
    logger.info("Scanning for pending applications older than %s", cutoff.isoformat())

    db = SessionLocal()
    try:
        apps = (
            db.query(Application)
            .filter(Application.application_status == "pending")
            .filter(Application.created_at < cutoff)
            .all()
        )
        logger.info("Found %d stale applications", len(apps))

        for app in apps:
            url = f"{API_BASE}/{app.application_id}/new_profile/"
            logger.info("POST %s", url)
            r = requests.post(url)
            if r.status_code == 200:
                logger.info("✅ Queued via API: %s", r.json())
            else:
                logger.error("❌ Failed to queue %s: %s", app.application_id, r.text)
    finally:
        db.close()

if __name__ == "__main__":
    run_scan()