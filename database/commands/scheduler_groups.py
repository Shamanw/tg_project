from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import SchedulerGroup



async def add_scheduler_group(unique_id: int, group_id: int, period: int, period_minutes: int):
    async with get_session() as session:
        sql = SchedulerGroup(unique_id=unique_id, group_id=group_id, period=period, period_minutes=period_minutes, added_at=datetime.now(), next_sended_at=datetime.now() + timedelta(hours=period))
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_scheduler_group(unique_id: int = None, group_id: int = None, period: int = None, period_minutes: int = None):
    async with get_session() as session:
        sql = select(SchedulerGroup)
        if unique_id:
            sql = sql.where(SchedulerGroup.unique_id == unique_id)
        if group_id:
            sql = sql.where(SchedulerGroup.group_id == group_id)
        if period:
            sql = sql.where(SchedulerGroup.period == period)
        if period_minutes:
            sql = sql.where(SchedulerGroup.period_minutes == period_minutes)
        result = await session.execute(sql)
        return result.scalar()


async def select_scheduler_groups(unique_id: int = None, group_id: int = None, period: int = None, period_minutes: int = None, current_time = None):
    async with get_session() as session:
        sql = select(SchedulerGroup)
        if unique_id:
            sql = sql.where(SchedulerGroup.unique_id == unique_id)
        if group_id:
            sql = sql.where(SchedulerGroup.group_id == group_id)
        if period:
            sql = sql.where(SchedulerGroup.period == period)
        if period_minutes:
            sql = sql.where(SchedulerGroup.period_minutes == period_minutes)
        if current_time:
            sql = sql.where(SchedulerGroup.next_sended_at <= current_time)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_scheduler_group(unique_id: int = None, group_id: int = None, period: int = None, period_minutes: int = None, data: dict = None):
    async with get_session() as session:
        sql = update(SchedulerGroup)
        if unique_id:
            sql = sql.where(SchedulerGroup.unique_id == unique_id)
        if group_id:
            sql = sql.where(SchedulerGroup.group_id == group_id)
        if period:
            sql = sql.where(SchedulerGroup.period == period)
        if period_minutes:
            sql = sql.where(SchedulerGroup.period_minutes == period_minutes)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_scheduler_group(unique_id: int = None, group_id: int = None, period: int = None, period_minutes: int = None):
    async with get_session() as session:
        sql = delete(SchedulerGroup)
        if unique_id:
            sql = sql.where(SchedulerGroup.unique_id == unique_id)
        if group_id:
            sql = sql.where(SchedulerGroup.group_id == group_id)
        if period:
            sql = sql.where(SchedulerGroup.period == period)
        if period_minutes:
            sql = sql.where(SchedulerGroup.period_minutes == period_minutes)
        await session.execute(sql)
        await session.commit()

