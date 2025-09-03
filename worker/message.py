import common.models.message as message
import common.models.batch as batch
import common.models.job as job
from common.db import *
import time
import random

random.seed(time.time_ns())

async def process_message(bid: int):
     time.sleep(1)
     async with AsyncSessionLocal() as db:
        async with db.begin():
            try:
                batch_record: batch.Batch = await batch.get_batch_by_id(db=db, id=bid)

                if random.random() < 0.05:
                    print('error 2')
                    raise ValueError("randomly generated error 2")

                msg = await message.create_message(
                    db=db,
                    content=batch_record.payload['content'],
                    status='processed'
                )

                if random.random() < 0.5:
                    print('catastrophe 1')
                    exit(1)

                await batch.update_batch_status_by_id(db=db, id=bid, new_status='done')

                if random.random() < 0.05:
                    print('error 1')
                    raise ValueError("randomly generated error 1")

                await job.update_job_status_by_job_id(
                    db=db,
                    job_id=batch_record.job_id,
                    new_status="done"
                )
            except Exception as e:
                db.rollback()
                raise
        
    
