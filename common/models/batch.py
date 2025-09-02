from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Index
from sqlalchemy.orm import relationship
from common.db import *

from datetime import datetime
import uuid

class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.job_id"), nullable=False)
    batch_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    payload = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    __table_args__ = (
        Index("idx_batches_jobid_batchid", "job_id", "batch_id"),
    )


async def create_batch(db: AsyncSession, job_id: str, batch_id: int, payload: dict, status: str = 'pending', result: dict = None, error: str = None):
    new_batch = Batch(job_id=job_id, batch_id=batch_id, status=status, payload=payload, result=result, error=error)
    try:
        db.add(new_batch)
        await db.flush()
        await db.refresh(new_batch)
        return new_batch
    except Exception as e:
        print(f"Error creating batch: {e}")
        await db.rollback()
        raise e
    
async def update_batch_status_by_id(db: AsyncSession, id: int, new_status: str):
    print('Start update')
    try:
        result = await db.execute(
            sqlalchemy.select(Batch).where(Batch.id == id)
        )
        batch = result.scalars().first()
        if batch:
            batch.status = new_status or batch.status
            await db.flush()
            await db.refresh(batch)
            print(f'returned successfully, new status: {batch.status}')
            return batch
        print("didn't find batch")
        return None
    except Exception as e:
        print(f"Error updating batch: {e}")
        await db.rollback()
        raise e
        
async def update_batch_status_by_batch_id(db: AsyncSession, batch_id: int, new_status: str):
    print('Start update')
    try:
        result = await db.execute(
            sqlalchemy.select(Batch).where(Batch.batch_id == batch_id)
        )
        batch = result.scalars().first()
        if batch:
            batch.status = new_status or batch.status
            await db.flush()
            await db.refresh(batch)
            print(f'returned successfully, new status: {batch.status}')
            return batch
        print("didn't find batch")
        return None
    except Exception as e:
        print(f"Error updating batch: {e}")
        await db.rollback()
        raise e

async def get_batch_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Batch).where(Batch.id == id)
        )
        batch = result.scalars().first()
        return batch
    except Exception as e:
        print(f"Error retrieving batch: {e}")
        raise e
    
async def get_batch_by_batch_id(db: AsyncSession, batch_id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Batch).where(Batch.id == batch_id)
        )
        batch = result.scalars().first()
        return batch
    except Exception as e:
        print(f"Error retrieving batch: {e}")
        raise e
    
async def delete_batch(db: AsyncSession, id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Batch).where(Batch.id == id)
        )
        batch = result.scalars().first()
        if batch:
            await db.delete(batch)
            await db.flush()
            return True
        return False
    except Exception as e:
        print(f"Error deleting batch: {e}")
        await db.rollback()
        raise e


if __name__ == "__main__":
    ping()