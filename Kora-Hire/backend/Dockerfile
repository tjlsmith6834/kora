# backend/Dockerfile
FROM python:3.13-slim
WORKDIR /app

# only dependency layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

###Necessary for AWS
# Expose the port your app listens on
EXPOSE 8000

# Run uvicorn in the foreground
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]