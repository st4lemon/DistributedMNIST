import asyncio
import redis.asyncio as aioredis
from db.db import *
import db.models.message as message

async def worker():
    
    redis = await aioredis.from_url("redis://localhost:6379")
    pubsub = redis.pubsub()
    await pubsub.subscribe("messages")

    print("Worker started, waiting for messages...")
    async for msg in pubsub.listen():
        if msg['type'] == 'message':
            print(f"Received message: {msg['data'].decode()}")

            async with AsyncSessionLocal() as db:
                msg_record = await message.get_message_by_content(db=db, content=msg['data'].decode())
                print("Done getting")
                await message.update_message(db=db, message_id=msg_record.id, new_status="processed")
                print("Done updating")
                await db.commit()
        print('Done with current message, ready for new one')

if __name__ == "__main__":
    asyncio.run(worker())