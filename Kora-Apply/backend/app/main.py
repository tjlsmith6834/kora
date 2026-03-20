from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
import logging

# Import config
from .config import config

# Import routers & database connection
from .routers.applications import router as applications_router
from .routers.jobs import router as jobs_router
from .routers.surveys import router as surveys_router
from .routers.tasks import router as tasks_router

# Initialize FastAPI app
app = FastAPI(
    title="Kora-Apply API",
    version="1.0.0",
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info(f"Starting API in {'Development' if config.DEBUG else 'Production'} mode")

# Middleware for CORS (Uses values from config.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

logging.info(f"Allowed CORS origins: {config.ALLOWED_ORIGINS}")

# GZip Middleware for better performance (Compress responses)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include Routers
app.include_router(applications_router)
app.include_router(jobs_router)
app.include_router(surveys_router)
app.include_router(tasks_router)

# Health Check Endpoint
@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "message": "Service is healthy"}

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Kora!"}