# distributedMNIST

### Goals
- Learn Redis and Docker
- Coordinate multiple services using Docker-Compose
- Push to AWS and host online

## Installation

Running on Python 3.12 and Ubuntu 22.04
Also: FastAPI, Postgres, Redis

### Local setup

- Create a virtual environment with your chosen python installation: `python3.12 -m venv venv`
- Actiavte the environment: `source venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Run local start script (TODO)

### Docker setup

- Pull Docker image 
- Run docker start script (TODO)

# Structure

### backend
API service to receive data for inference and provide status and results of submitted jobs

### db
Database service 
- `USERS`: stores information on users submitting jobs
- `JOB`: stores overall status of a job: processing, completed, error
- `BATCH`: stores results of batches indexed first by job id, then by batch index. We can query a window of results from the job by using a range-search on a tree index



# Changelog
- 8/29/2025: Initial commit, set up simple redis demo for workers

### TODO
- Set up Dockerfiles for backend and worker, and Docker-compose for the whole repo
- Run a skeleton job locally with a Redis image running in a Docker container, to ensure you know how to send messages with Redis. 