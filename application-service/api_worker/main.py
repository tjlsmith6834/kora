from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import logging
import time

# Configure logging format
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

root = logging.getLogger()
root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

from api_worker.routers.applications import router as applications_router
from api_worker.routers.tasks import router as tasks_router

app = FastAPI()
app.include_router(applications_router)
app.include_router(tasks_router)

# Middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logging.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Response status: {response.status_code} (Processed in {process_time:.2f}s)")
    return response


# Exception handler to capture and log all errors
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logging.error(f"❌ Exception in request {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

@app.get("/health", status_code=200)
async def health_check():
    logging.info("Received health check request")
    return {"status": "ok", "message": "Service is healthy"}

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Kora's application service!"}