# Use a minimal Python base image
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

# Copy requirements file first to optimize Docker layer caching
COPY api/requirements.txt .

# Install dependencies (assumes requirements.txt includes FastAPI, Uvicorn, etc.)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY api /app/api

# Set environment variable so Python can find models_schemas
ENV PYTHONPATH="/app"

# Ensure the non-root user exists for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set permissions for /app directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

###Necessary for AWS
# Expose the port your app listens on
EXPOSE 8003

# Run uvicorn in the foreground
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8003"]