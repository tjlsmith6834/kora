# Use a minimal Python base image for efficiency
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for database connectivity (e.g., PostgreSQL)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the shared library first
COPY common /app/common

# Copy requirements file first (to optimize Docker layer caching)
COPY celery_worker/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY celery_worker /app/celery_worker

# Set environment variable so Python can find models_schemas
ENV PYTHONPATH="/app"

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set permissions for /app directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Set working directory for startup
WORKDIR /app/celery_worker

# Run Celery worker
CMD ["celery", "-A", "common.celery_config.celery_app", "worker", "--loglevel=info"]