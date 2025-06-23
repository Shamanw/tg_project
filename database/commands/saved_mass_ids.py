from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import SavedMassIds


async def add_saved_mass_ids(ids: str, message_id: int):
    async with get_session() as session:
        sql = SavedMassIds(ids=ids, message_id=message_id, added_at=datetime.now())
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_saved_mass_ids(message_id: int = None):
    async with get_session() as session:
        sql = select(SavedMassIds)
        if message_id:
            sql = sql.where(SavedMassIds.message_id == message_id)
        result = await session.execute(sql)
        return result.scalar()


async def select_saved_mass_idss():
    async with get_session() as session:
        result = await session.execute(select(SavedMassIds))
        results = result.scalars().all()
        return results


async def update_saved_mass_ids(message_id: int = None, data: dict = None):
    async with get_session() as session:
        sql = update(SavedMassIds)
        if message_id:
            sql = sql.where(SavedMassIds.message_id == message_id)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_saved_mass_ids(message_id: int = None):
    async with get_session() as session:
        sql = delete(SavedMassIds)
        if message_id:
            sql = sql.where(SavedMassIds.message_id == message_id)
        await session.execute(sql)
        await session.commit()

