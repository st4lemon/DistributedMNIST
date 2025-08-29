from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as aioredis

async def lifespan(app: FastAPI):
    # Startup code

    global redis
    redis = await aioredis.from_url("redis://localhost:6379")
    print("Starting up...")

    yield

    # cleanup resources, close connections, etc. 
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def ping():
    return {"message": "pong"}

@app.post("/message")
async def send_pubsub_message(message: str):
    # publishes a message to subscribers
    await redis.publish("messages", message)
    return {"message": f"Message '{message}' sent to subscribers."}