from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from database.engine import get_session
from database.tables import ExceptionPhone


async def add_exception_phone(phone_number: int):
    async with get_session() as session:
        sql = ExceptionPhone(
            phone_number=phone_number,
            added_at=datetime.now()
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_exception_phone(phone_number: int = None):
    async with get_session() as session:
        sql = select(ExceptionPhone)
        if phone_number is not None:
            sql = sql.where(ExceptionPhone.phone_number == phone_number)
        result = await session.execute(sql)
        return result.scalar()


async def select_exception_phones():
    async with get_session() as session:
        result = await session.execute(select(ExceptionPhone))
        results = result.scalars().all()
        return results


async def update_exception_phone(phone_number: int = None, data: dict = None):
    async with get_session() as session:
        sql = update(ExceptionPhone)
        if phone_number is not None:
            sql = sql.where(ExceptionPhone.phone_number == phone_number)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_exception_phone(phone_number: int = None):
    async with get_session() as session:
        sql = delete(ExceptionPhone)
        if phone_number is not None:
            sql = sql.where(ExceptionPhone.phone_number == phone_number)
        await session.execute(sql)
        await session.commit()

