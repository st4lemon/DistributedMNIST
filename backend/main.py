from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from redis.exceptions import ResponseError
import redis.asyncio as redis
import os
import common.models.message as message
from common.db import *
from common.redis_client import get_redis

load_dotenv()

STREAM_NAME = "messages"
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

    app.state.redis = await get_redis()
    await initialize_db()
    await create_consumer_group(app.state.redis)

    print("Starting up...")

    yield

    # cleanup resources, close connections, etc. 
    await app.state.redis.close()
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def ping():
    return {"message": "pong"}

@app.post("/message")
async def send_pubsub_message(msg: str, db: AsyncSession = Depends(get_db), redis_client=Depends(lambda: app.state.redis)): 
    # publishes a message to subscribers
    msg = await message.create_message(db, content=msg)
    await redis_client.xadd(STREAM_NAME, {"message_id": str(msg.id), "content": str(msg.content)})
    return {"message": f"Message '{msg.content}' sent to subscribers."}