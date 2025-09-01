import asyncio
import redis.asyncio as red
from common.db import *
import common.models.message as message
import common.models.job as job
import common.models.batch as batch
from common.redis_client import get_redis
from dotenv import load_dotenv

import os

load_dotenv()

print("worker loading")

STREAM_NAME = "jobs"
CONSUMER_GROUP = "workers"
CONSUMER_NAME = f"worker-{os.getenv('HOSTNAME')}"

async def worker():
    
    print("Entered worker", CONSUMER_NAME)
    redis = await get_redis()

    print("Worker started, waiting for messages...", flush=True)
    while True:
        resp = await redis.xreadgroup( 
            groupname=CONSUMER_GROUP,
            consumername=CONSUMER_NAME,
            streams={STREAM_NAME: ">"},
            count=1,
            block=5000
        )
        if resp:
            stream, messages = resp[0]
            for msg_id, fields in messages:
                print("Got message:", fields)

                async with AsyncSessionLocal() as db:
                    await message.update_message(
                        db,
                        message_id=int(fields["message_id"]),
                        new_status="processed"
                    )
                
                await redis.xack(STREAM_NAME, CONSUMER_GROUP, msg_id)


if __name__ == "__main__":
    print("Starting worker:")
    asyncio.run(worker())