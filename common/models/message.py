from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from common.db import *

import datetime

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    sent = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, default='sent')



async def create_message(db: AsyncSession, content: str, status: str = 'sent'):
    new_message = Message(content=content)
    try:
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)
        return new_message
    except Exception as e:
        print(f"Error creating message: {e}")
        await db.rollback()
        return None
    
async def update_message(db: AsyncSession, message_id: int, new_content: str = None, new_status: str = None):
    print('Start update')
    try:
        result = await db.execute(
            sqlalchemy.select(Message).where(Message.id == message_id)
        )
        message = result.scalars().first()
        if message:
            message.content = new_content or message.content
            message.status = new_status or message.status
            await db.commit()
            await db.refresh(message)
            print(f'returned successfully, new status: {message.status}')
            return message
        print("didn't find message")
        return None
    except Exception as e:
        print(f"Error updating message: {e}")
        await db.rollback()
        return None

async def get_message_by_id(db: AsyncSession, message_id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Message).where(Message.id == message_id)
        )
        message = result.scalars().first()
        return message
    except Exception as e:
        print(f"Error retrieving message: {e}")
        return None
    
async def get_message_by_content(db: AsyncSession, content: str):
    print('Start get by content')
    try:
        result = await db.execute(
            sqlalchemy.select(Message).where(Message.content == content)
        )
        message = result.scalars().first()
        return message
    except Exception as e:
        print(f"Error retrieving message: {e}")
        return None

async def delete_message(db: AsyncSession, message_id: int):
    try:
        result = await db.execute(
            sqlalchemy.select(Message).where(Message.id == message_id)
        )
        message = result.scalars().first()
        if message:
            await db.delete(message)
            await db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting message: {e}")
        await db.rollback()
        return False    


if __name__ == "__main__":
    ping()