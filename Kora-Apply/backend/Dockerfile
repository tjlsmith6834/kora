# backend/Dockerfile

FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8001

# Run with production-grade server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]