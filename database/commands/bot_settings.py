from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import BotSetting


async def add_bot_setting():
    async with get_session() as session:
        sql = BotSetting()
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_bot_setting(primary_id: int = 1):
    async with get_session() as session:
        sql = select(BotSetting)
        if primary_id:
            sql = sql.where(BotSetting.id == primary_id)
        result = await session.execute(sql)
        return result.scalar()


async def select_bot_settings(primary_id: int = 1):
    async with get_session() as session:
        sql = select(BotSetting)
        if primary_id:
            sql = sql.where(BotSetting.id == primary_id)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_bot_setting(primary_id: int = 1, data: dict = None):
    async with get_session() as session:
        sql = update(BotSetting)
        if primary_id:
            sql = sql.where(BotSetting.id == primary_id)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_bot_setting(primary_id: int = 1):
    async with get_session() as session:
        sql = delete(BotSetting)
        if primary_id:
            sql = sql.where(BotSetting.id == primary_id)
        await session.execute(sql)
        await session.commit()

