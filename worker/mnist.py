import common.models.message as message
import common.models.batch as batch
import common.models.job as job
from common.db import *
import time
import random

random.seed(time.time_ns())

async def process_mnist(bid: int):
     async with AsyncSessionLocal() as db:
        async with db.begin():
            try:
                batch_record: batch.Batch = await batch.get_batch_by_id(db=db, id=bid)
                print("processing mnist")
                await batch.update_batch_status_by_id(db=db, id=bid, new_status='done')

                await job.update_job_status_by_job_id(
                    db=db,
                    job_id=batch_record.job_id,
                    new_status="done"
                )
            except Exception as e:
                db.rollback()
                raise
        
    
