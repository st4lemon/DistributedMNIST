import common.models.message as message
import common.models.batch as batch
import common.models.job as job
from common.db import *
import time
import random
from dotenv import load_dotenv
import os

load_dotenv()

random.seed(time.time_ns())

fail = os.getenv("WORKER_FAIL") == 'true'

async def process_message(bid: int):
     time.sleep(1)
     async with AsyncSessionLocal() as db:
        async with db.begin():
            try:
                batch_record: batch.Batch = await batch.get_batch_by_id(db=db, id=bid)

                if random.random() < 0.05 and fail:
                    print('error 2')
                    raise ValueError("randomly generated error 2")

                msg = await message.create_message(
                    db=db,
                    content=batch_record.payload['content'],
                    status='processed'
                )

                if random.random() < 0.05 and fail:
                    print('catastrophe 1')
                    exit(1)

                await batch.update_batch_status_by_id(db=db, id=bid, new_status='done')

                if random.random() < 0.05 and fail:
                    print('error 1')
                    raise ValueError("randomly generated error 1")

                await job.update_job_status_by_job_id(
                    db=db,
                    job_id=batch_record.job_id,
                    new_status="done"
                )
            except Exception as e:
                await db.rollback()
                raise e
        
    
