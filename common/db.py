# Generic methods for DB connections, table schemas and models, etc. 
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import asyncpg
import os

print('db loading env')
load_dotenv()

print('db done loading env')
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@postgres:5432/mnist_db'
print("database url:", DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=180,
    future=True   
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)    

Base = declarative_base()

async def initialize_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def ping():
    print('pong')


