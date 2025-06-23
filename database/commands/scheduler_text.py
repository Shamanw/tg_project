from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import SchedulerText


async def add_scheduler_text(unique_id: int, text: str, file_name: str):
    async with get_session() as session:
        sql = SchedulerText(unique_id=unique_id, text=text, file_name=file_name, added_at=datetime.now())
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_scheduler_text(unique_id: int = None):
    async with get_session() as session:
        sql = select(SchedulerText)
        if unique_id:
            sql = sql.where(SchedulerText.unique_id == unique_id)
        result = await session.execute(sql)
        return result.scalar()


async def select_scheduler_texts():
    async with get_session() as session:
        result = await session.execute(select(SchedulerText))
        results = result.scalars().all()
        return results


async def update_scheduler_text(unique_id: int = None, data: dict = None):
    async with get_session() as session:
        sql = update(SchedulerText)
        if unique_id:
            sql = sql.where(SchedulerText.unique_id == unique_id)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_scheduler_text(unique_id: int = None):
    async with get_session() as session:
        sql = delete(SchedulerText)
        if unique_id:
            sql = sql.where(SchedulerText.unique_id == unique_id)
        await session.execute(sql)
        await session.commit()

