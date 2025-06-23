from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import Application

async def add_application(user_id: int):
    async with get_session() as session:
        sql = Application(user_id=user_id, sended_at=datetime.now())
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql

async def select_application(primary_id: int = None, user_id: int = None):
    async with get_session() as session:
        if primary_id:
            value = Application.id == primary_id
        elif user_id:
            value = Application.user_id == user_id
        sql = select(Application).where(value).order_by(Application.sended_at.desc())
        result = await session.execute(sql)
        return result.scalar()

async def select_applications(user_id: int):
    async with get_session() as session:
        # result = await session.execute(select(Application).where(Application.user_id == user_id).where(Application.sended_at >= datetime.now() - timedelta(hours=24)))
        result = await session.execute(select(Application).where(Application.user_id == user_id))
        results = result.scalars().all()
        return results

async def update_application(primary_id: int = None, user_id: int = None, data: dict = None):
    async with get_session() as session:
        if primary_id:
            value = Application.id == primary_id
        elif user_id:
            value = Application.user_id == user_id
        sql = update(Application).where(value).values(data)
        await session.execute(sql)
        await session.commit()
