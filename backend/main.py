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
from common.redis_client import *

load_dotenv()

async def lifespan(app: FastAPI):
    # Startup code
    print("Just started")
    app.state.redis_client = RedisClient()
    app.state.redis = await app.state.redis_client.get_redis()
    print("Got redis")
    await initialize_db()
    print("Got db")
    await app.state.redis_client.create_consumer_group(
        stream = app.state.redis_client.JOB_STREAM,
        group = app.state.redis_client.JOB_GROUP
    )

    await app.state.redis_client.create_consumer_group(
        stream = app.state.redis_client.JOB_DLQ,
        group = app.state.redis_client.JOB_DLQ_GROUP
    )

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
        
        groups = await redis_client.xinfo_groups(app.state.redis_client.JOB_STREAM)
        print(groups)
        if not any(g['name'] == app.state.redis_client.JOB_GROUP for g in groups):
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
    async with db.begin():
        try:
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
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    'error': f"Exception occurred: {e}"
                }
            )
        
    await redis_client.xadd(app.state.redis_client.JOB_STREAM, { "id": str(batch_record.id), "job_type": "message" })
    return { "job_id": str(job_record.job_id) }

