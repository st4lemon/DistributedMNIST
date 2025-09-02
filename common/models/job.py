from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Index
from sqlalchemy.orm import relationship
from common.db import *

from datetime import datetime
import uuid

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, nullable=False, unique=True, default=lambda: str(uuid.uuid4()), index=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    job_metadata = Column(JSON, nullable=True) # size of dataset, number of batches, etc. 
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    

async def create_job(db: AsyncSession, job_type: str, job_metadata: dict, status: str = 'pending'):
    new_job = Job(job_type=job_type, job_metadata=job_metadata, status=status)
    try:
        db.add(new_job)
        await db.flush()
        await db.refresh(new_job)
        return new_job
    except Exception as e:
        print(f"Error creating job: {e}")
        await db.rollback()
        raise e
    
async def update_job_status_by_id(db: AsyncSession, id: int, new_status: str):
    print('Start update')
    try:
        result = await db.execute(
            sqlalchemy.select(Job).where(Job.id == id)
        )
        job = result.scalars().first()
        if job:
            job.status = new_status or job.status
            await db.flush()
            await db.refresh(job)
            print(f'returned successfully, new status: {job.status}')
            return job
        print("didn't find job")
        return None
    except Exception as e:
        print(f"Error updating job: {e}")
        await db.rollback()
        raise e
        
async def update_job_status_by_job_id(db: AsyncSession, job_id: int, new_status: str):
    print('Start update')
    try:
        result = await db.execute(
            sqlalchemy.select(Job).where(Job.job_id == job_id)
        )
        job = result.scalars().first()
        if job:
            job.status = new_status or job.status
            await db.flush()
            await db.refresh(job)
            print(f'returned successfully, new status: {job.status}')
            return job
        print("didn't find job")
        return None
    except Exception as e:
        print(f"Error updating job: {e}")
        await db.rollback()
        raise e

async def get_job_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Job).where(Job.id == id)
        )
        job = result.scalars().first()
        return job
    except Exception as e:
        print(f"Error retrieving job: {e}")
        raise e
    
async def get_job_by_job_id(db: AsyncSession, job_id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Job).where(Job.id == job_id)
        )
        job = result.scalars().first()
        return job
    except Exception as e:
        print(f"Error retrieving job: {e}")
        raise e
    
async def delete_job(db: AsyncSession, id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Job).where(Job.id == id)
        )
        job = result.scalars().first()
        if job:
            await db.delete(job)
            await db.flush()
            return True
        return False
    except Exception as e:
        print(f"Error deleting job: {e}")
        await db.rollback()
        raise e   


if __name__ == "__main__":
    ping()