# base image
FROM python:3.12-slim AS base

# declare working directory inside the container
WORKDIR /app

# install ubuntu dependencies
RUN apt-get update && \
    apt-get install -y curl build-essential python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# API service
FROM base AS api 
WORKDIR /app
COPY backend /app/backend
COPY common /app/common

# Expose API port
EXPOSE 8000 

# Run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Worker service
FROM base AS worker
WORKDIR /app
COPY worker /app/worker
COPY common /app/common

# Run Worker
CMD ["python", "-m", "worker.main"]


# Reclaimer service
FROM base AS reclaimer
WORKDIR /app
COPY reclaimer /app/reclaimer
COPY common /app/common

# Run Worker
CMD ["python", "-m", "reclaimer.main"]


