from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
import os
import db.models.message as message
from db.db import *

load_dotenv()

async def lifespan(app: FastAPI):
    # Startup code

    await initialize_db()

    global redis
    redis = await aioredis.from_url(f"{os.getenv('REDIS_URL')}")
    print("Starting up...")

    yield

    # cleanup resources, close connections, etc. 
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def ping():
    return {"message": "pong"}

@app.post("/message")
async def send_pubsub_message(msg: str, db: AsyncSession = Depends(get_db)): 
    # publishes a message to subscribers
    await message.create_message(db, content=msg)
    await redis.publish("messages", msg)
    return {"message": f"Message '{msg}' sent to subscribers."}