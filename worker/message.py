import common.models.message as message
import common.models.batch as batch
import common.models.job as job
from common.db import *
import time

async def process_message(bid: int):
     time.sleep(1)
     async with AsyncSessionLocal() as db:
        async with db.begin():
            batch_record: batch.Batch = await batch.get_batch_by_id(db=db, id=bid)

            msg = await message.create_message(
                db=db,
                content=batch_record.payload['content'],
                status='processed'
            )

            await batch.update_batch_status_by_id(db=db, id=bid, new_status='done')

            await job.update_job_status_by_job_id(
                db=db,
                job_id=batch_record.job_id,
                new_status="done"
            )
        
    
