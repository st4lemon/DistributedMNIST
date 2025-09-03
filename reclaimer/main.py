import asyncio
import redis.asyncio as redis
from common.db import *
import common.models.message as message
import common.models.job as job
import common.models.batch as batch
from common.redis_client import *
from dotenv import load_dotenv 

import os

load_dotenv()

print("reclaimer loading")

CONSUMER_NAME = f"reclaimer-{os.getenv('HOSTNAME')}"

async def reclaimer():

    print("Entered reclaimer", CONSUMER_NAME)
    redis_client = RedisClient()
    r = await redis_client.get_redis()

    print("Reclaimer started, waiting for failed tasks...", flush=True)
    last_id = "0-0"

    while True:
        resp = await r.xautoclaim(
            name=redis_client.JOB_STREAM,
            groupname=redis_client.JOB_GROUP,
            consumername=CONSUMER_NAME,
            min_idle_time=20000,
            start_id=last_id,
            count=1
        )

        if resp:
            last_id, messages, _ = resp
            for msg_id, fields in messages:
                print("Reclaimed message:", fields, flush=True)
                
                retries = int(fields['retries'])+1
                if retries >= 5:
                    await r.xadd(redis_client.JOB_DLQ, { "id": int(fields['id']), "job_type": fields['job_type'], "retries": retries })
                else:
                    await r.xadd(redis_client.JOB_STREAM, { "id": int(fields['id']), "job_type": fields['job_type'], "retries": retries })
                await r.xack(redis_client.JOB_STREAM, redis_client.JOB_GROUP, msg_id)

if __name__ == "__main__":
    print("Starting reclaimer:")
    asyncio.run(reclaimer())