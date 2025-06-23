from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import SchedulerBot



async def add_scheduler_bot(unique_id: int, period: int, period_minutes: int):
    async with get_session() as session:
        sql = SchedulerBot(unique_id=unique_id, period=period, period_minutes=period_minutes, added_at=datetime.now(), next_sended_at=datetime.now() + timedelta(hours=period))
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_scheduler_bot(unique_id: int = None, period: int = None, period_minutes: int = None):
    async with get_session() as session:
        sql = select(SchedulerBot)
        if unique_id:
            sql = sql.where(SchedulerBot.unique_id == unique_id)
        if period:
            sql = sql.where(SchedulerBot.period == period)
        if period_minutes:
            sql = sql.where(SchedulerBot.period_minutes == period_minutes)
        result = await session.execute(sql)
        return result.scalar()


async def select_scheduler_bots(unique_id: int = None, period: int = None, period_minutes: int = None, current_time = None):
    async with get_session() as session:
        sql = select(SchedulerBot)
        if unique_id:
            sql = sql.where(SchedulerBot.unique_id == unique_id)
        if period:
            sql = sql.where(SchedulerBot.period == period)
        if period_minutes:
            sql = sql.where(SchedulerBot.period_minutes == period_minutes)
        if current_time:
            sql = sql.where(SchedulerBot.next_sended_at <= current_time)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_scheduler_bot(unique_id: int = None, period: int = None, period_minutes: int = None, data: dict = None):
    async with get_session() as session:
        sql = update(SchedulerBot)
        if unique_id:
            sql = sql.where(SchedulerBot.unique_id == unique_id)
        if period:
            sql = sql.where(SchedulerBot.period == period)
        if period_minutes:
            sql = sql.where(SchedulerBot.period_minutes == period_minutes)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_scheduler_bot(unique_id: int = None, period: int = None, period_minutes: int = None):
    async with get_session() as session:
        sql = delete(SchedulerBot)
        if unique_id:
            sql = sql.where(SchedulerBot.unique_id == unique_id)
        if period:
            sql = sql.where(SchedulerBot.period == period)
        if period_minutes:
            sql = sql.where(SchedulerBot.period_minutes == period_minutes)
        await session.execute(sql)
        await session.commit()

