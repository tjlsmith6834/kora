from fastapi import FastAPI
import logging

from .routers.jobs import router as jobs_router
from .routers.rubrics import router as rubrics_router
from .routers.tasks import router as tasks_router

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()
app.include_router(jobs_router)
app.include_router(rubrics_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Kora's jobs service"}
@app.get("/health", status_code=200)
async def health_check():
    logging.info("Received health check request")
    return {"status": "ok", "message": "Service is healthy"}
