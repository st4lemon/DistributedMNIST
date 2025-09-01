from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from redis.exceptions import ResponseError
import redis.asyncio as redis
import os
import common.models.message as message
import common.models.job as job
import common.models.batch as batch
from common.db import *
from common.redis_client import get_redis

load_dotenv()

STREAM_NAME = "jobs"
CONSUMER_GROUP = "workers"

async def create_consumer_group(redis_client: redis.Redis):
    """
    Creates a Redis stream consumer group if it doesn't exist.
    """
    try:
        # '$' means start reading only new messages
        await redis_client.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="$", mkstream=True)
        print(f"Consumer group '{CONSUMER_GROUP}' created on stream '{STREAM_NAME}'.")
    except ResponseError as e:
        if "BUSYGROUP" in str(e):
            # Group already exists
            print(f"Consumer group '{CONSUMER_GROUP}' already exists.")
        else:
            raise

async def lifespan(app: FastAPI):
    # Startup code
    print("Just started")
    app.state.redis = await get_redis()
    print("Got redis")
    await initialize_db()
    print("Got db")
    await create_consumer_group(app.state.redis)

    print("Starting up...")

    yield

    # cleanup resources, close connections, etc. 
    await app.state.redis.close()
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def ping(redis_client=Depends(lambda: app.state.redis)):
    try:
        pong = await redis_client.ping()
        if not pong:
            print("Redis not responding")
            raise HTTPException(status_code=503, detail="Redis not responding")
        
        groups = await redis_client.xinfo_groups(STREAM_NAME)
        print(groups)
        if not any(g['name'] == CONSUMER_GROUP for g in groups):
            print("Consumer group not ready")
            raise HTTPException(status_code=503, detail="Consumer group not ready")
        return JSONResponse(
            content={"message": "pong"},
            status_code=200
        )
    except Exception as e:
        print(f"Redis error: {e}")
        raise HTTPException(status_code=503, detail=f"Redis error: {e}")
    
    

@app.post("/message")
async def send_pubsub_message(msg: str, db: AsyncSession = Depends(get_db), redis_client=Depends(lambda: app.state.redis)): 
    # publishes a message to subscribers

    job_record = await job.create_job(
        db=db, 
        job_type="message",
        job_metadata={
            'batch_count': 1,
            'batch_size': 1
        }
    )
    
    batch_record = await batch.create_batch(
        db=db,
        job_id=job_record.job_id,
        batch_id=0,
        payload= {
            'content': msg
        }
    )

    await redis_client.xadd(STREAM_NAME, { "id": str(batch_record.id), "job_type": "message" })
    return { "job_id": str(job_record.job_id) }

