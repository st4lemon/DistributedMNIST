from redis.exceptions import ResponseError
import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

class RedisClient():

    def __init__(self):
        self.redis_client: redis.Redis | None = None 
        
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        self.JOB_STREAM = 'jobs'
        self.JOB_GROUP = 'workers'
        self.JOB_DLQ = 'jobs-dlq'
        self.JOB_DLQ_GROUP = 'workers-dlq'


    async def get_redis(self) -> redis.Redis:
        if not self.redis_client:
            self.redis_client = redis.Redis(host=self.REDIS_HOST, port=self.REDIS_PORT, decode_responses=True)
        return self.redis_client

    async def create_consumer_group(self, stream: str, group: str):
        try:
            await self.redis_client.xgroup_create(stream, group, id="$", mkstream=True)
            print(f"Consumer group '{group}' created on stream '{stream}'.")
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                # Group already exists
                print(f"Consumer group '{group}' already exists.")
            else:
                raise