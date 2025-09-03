# distributedMNIST

### Goals
- Learn Redis and Docker
- Coordinate multiple services using Docker-Compose
- Push to AWS and host online

# Installation

Running on Python 3.12 and Ubuntu 22.04
Also: FastAPI, Postgres, Redis

## Local setup

- Create a virtual environment with your chosen python installation: `python3.12 -m venv venv`
- Actiavte the environment: `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Run local start script (TODO)

## Docker setup

Set up Docker network:
- `docker network create mnist-net`

To pull docker images:
- Pull api with `docker pull st4lemon/mnist-api`
- Pull worker with `docker pull st4lemon/mnist-worker`

To build images instead:
- Build api with `docker build -t st4lemon/mnist-api --target api .`
- Build worker with `docker build -t st4lemon/mnist-worker --target worker .`

Run containers:
- Run redis with `docker run --name redis --network mnist-net -p 6379:6379 redis`
- Run postgres with `docker run --name postgres --network mnist-net -p 5432:5432 --env-file .postgres.env -v pgdata:/var/lib/postgresql/data postgres:17`
- Run api with `docker run --name api --network mnist-net -p 8000:8000 --env-file .env st4lemon/mnist-api`
- Run worker with `docker run --name worker --network mnist-net --env-file .env st4lemon/mnist-worker`

Pushing docker images to repository:
- Create tags with `docker image tag <image_name> <image_name>:<tag>`
    - Example: `docker image tag st4lemon/mnist-api st4lemon/mnist-api:v1.0`
- Push with `docker image push --all-tags <image_name>`
    - Example: `docker image push --all-tags st4lemon/mnist-worker`

### Using docker-compose
Run `docker compose up --build` to build all images

# Structure

### backend
API service to receive data for inference and provide status and results of submitted jobs

### db
Database service 
- `USERS`: stores information on users submitting jobs
- `JOB`: stores overall status of a job: processing, completed, error
- `BATCH`: stores results of batches indexed first by job id, then by batch index. We can query a window of results from the job by using a range-search on a tree index



# Changelog
- 9/02/2025: Improved database/redis usage to support atomicity and retries
- 8/31/2025: Added support for docker-compose
- 8/30/2025: Created Dockerfile for API and Worker service, and configured connection between API, Worker, Redis, and Postgres. 
- 8/29/2025: Initial commit, set up simple redis demo for workers

### TODO
- Set up Dockerfiles for backend and worker, and Docker-compose for the whole repo
- Run a skeleton job locally with a Redis image running in a Docker container, to ensure you know how to send messages with Redis. 