import asyncio
import redis.asyncio as aioredis

async def worker():
    global redis
    redis = await aioredis.from_url("redis://localhost:6379")
    pubsub = redis.pubsub()
    await pubsub.subscribe("messages")

    print("Worker started, waiting for messages...")
    async for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received message: {message['data'].decode()}")

if __name__ == "__main__":
    asyncio.run(worker())