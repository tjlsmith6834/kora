from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase import initialize_firebase
import logging

from routers.applications import router as applications_router
from routers.jobs import router as jobs_router
from routers.smart_rubrics import router as smart_rubrics_router
from routers.tasks import router as tasks_router
from routers.accounts import router as accounts_router

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# Middleware for CORS (Uses values from config.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Uses list from config.py
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_firebase()

app.include_router(applications_router)
app.include_router(jobs_router)
app.include_router(smart_rubrics_router)
app.include_router(tasks_router)
app.include_router(accounts_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Kora Hire BFF!"}
@app.get("/health", status_code=200)
async def health_check():
    logging.info("Received health check request")
    return {"status": "ok", "message": "Service is healthy"}