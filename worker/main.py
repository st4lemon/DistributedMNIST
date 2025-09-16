import asyncio
import redis.asyncio as redis
from common.db import *
import common.models.message as message
import common.models.job as job
import common.models.batch as batch
from worker.message import *
from worker.mnist import *
from common.redis_client import *
from dotenv import load_dotenv

import os

load_dotenv()

print("worker loading")

CONSUMER_NAME = f"worker-{os.getenv('HOSTNAME')}"

async def worker():
    
    print("Entered worker", CONSUMER_NAME)
    redis_client = RedisClient()
    r = await redis_client.get_redis()

    print("Worker started, waiting for messages...", flush=True)
    while True:
        resp = await r.xreadgroup( 
            groupname=redis_client.JOB_GROUP,
            consumername=CONSUMER_NAME,
            streams={redis_client.JOB_STREAM: ">"},
            count=1,
            block=0
        )
        if resp:
            stream, messages = resp[0]
            for msg_id, fields in messages:
                print("Got message:", fields)
                bid = int(fields['id'])
                job_type = fields['job_type']
                retries = int(fields['retries'])

                try:
                    if job_type == "message":
                        await process_message(bid=bid)
                    if job_type == "mnist":
                        await process_mnist(bid=bid)
                except Exception as e:
                    # readd message to stream with retries
                    retries += 1
                    if retries >= 5:
                        await r.xadd(redis_client.JOB_DLQ, { "id": bid, "job_type": job_type, "retries": retries })
                    else:
                        await r.xadd(redis_client.JOB_STREAM, { "id": bid, "job_type": job_type, "retries": retries })
                
                await r.xack(redis_client.JOB_STREAM, redis_client.JOB_GROUP, msg_id)


if __name__ == "__main__":
    print("Starting worker:")
    asyncio.run(worker())