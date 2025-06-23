from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import Withdraw


async def add_withdraw(
        user_id = None,
        amount = None,
        writes = None,
        phones = None,
    ):
    async with get_session() as session:
        sql = Withdraw(
            user_id=user_id,
            amount=amount,
            writes=writes,
            phones=phones,
            created_at=datetime.now()
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_withdraw(
        primary_id = None,
        user_id = None,
        amount = None,
        withdraw_status = None,
        notify_status = None,
    ):
    async with get_session() as session:
        sql = select(Withdraw).limit(1).order_by(func.random()) 
        if primary_id is not None:
            sql = sql.where(Withdraw.id == primary_id)
        if user_id is not None:
            sql = sql.where(Withdraw.user_id == user_id)
        if amount is not None:
            sql = sql.where(Withdraw.amount == amount)
        if withdraw_status is not None:
            sql = sql.where(Withdraw.withdraw_status == withdraw_status)
        if notify_status is not None:
            sql = sql.where(Withdraw.notify_status == notify_status)
        result = await session.execute(sql)
        return result.scalar()


async def select_withdraws(
        user_id = None,
        amount = None,
        withdraw_status = None,
        notify_status = None,
        sort_asc = None,
        sort_desc = None,
):
    async with get_session() as session:
        sql = select(Withdraw)
        if user_id is not None:
            sql = sql.where(Withdraw.user_id == user_id)
        if amount is not None:
            sql = sql.where(Withdraw.amount == amount)
        if withdraw_status is not None:
            sql = sql.where(Withdraw.withdraw_status == withdraw_status)
        if notify_status is not None:
            sql = sql.where(Withdraw.notify_status == notify_status)
        if sort_asc:
            sql = sql.order_by(Withdraw.created_at.asc())
        if sort_desc:
            sql = sql.order_by(Withdraw.created_at.desc())
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_withdraw(
        primary_id = None,
        user_id = None,
        amount = None,
        withdraw_status = None,
        notify_status = None,
        data = None,
):
    async with get_session() as session:
        sql = update(Withdraw)
        if primary_id is not None:
            sql = sql.where(Withdraw.id == primary_id)
        if user_id is not None:
            sql = sql.where(Withdraw.user_id == user_id)
        if amount is not None:
            sql = sql.where(Withdraw.amount == amount)
        if withdraw_status is not None:
            sql = sql.where(Withdraw.withdraw_status == withdraw_status)
        if notify_status is not None:
            sql = sql.where(Withdraw.notify_status == notify_status)
        await session.execute(sql.values(data))
        await session.commit()

