from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import Payment


async def add_payment(
        user_id = None,
        from_address = None,
        usdt_address = None,
        transaction_hash = None,
        amount_usdt = None,
        timestamp = None
    ):
    async with get_session() as session:
        sql = Payment(
            user_id=user_id,
            from_address=from_address,
            usdt_address=usdt_address,
            transaction_hash=transaction_hash,
            amount_usdt=amount_usdt,
            timestamp=timestamp,
            added_at=datetime.now(),
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_payment(
        primary_id = None,
        user_id = None,
        from_address = None,
        usdt_address = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        timestamp = None,
        added_at_date_type = None
    ):
    async with get_session() as session:
        sql = select(Payment).limit(1)
        if primary_id is not None:
            sql = sql.where(Payment.id == int(primary_id))
        if user_id is not None:
            sql = sql.where(Payment.user_id == int(user_id))
        if from_address is not None:
            sql = sql.where(Payment.from_address == str(from_address))
        if usdt_address is not None:
            sql = sql.where(Payment.usdt_address == str(usdt_address))
        if transaction_hash is not None:
            sql = sql.where(Payment.transaction_hash == str(transaction_hash))
        if status is not None:
            sql = sql.where(Payment.status == status)
        if amount_usdt is not None:
            sql = sql.where(Payment.amount_usdt == amount_usdt)
        if timestamp is not None:
            sql = sql.where(Payment.timestamp == timestamp)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(Payment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(Payment.added_at >= start_date)
        result = await session.execute(sql)
        return result.scalar()


async def select_payments(
        user_id = None,
        not_user_id = None,
        from_address = None,
        usdt_address = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        timestamp = None,
        added_at_date_type = None
):
    async with get_session() as session:
        sql = select(Payment)
        if user_id is not None:
            sql = sql.where(Payment.user_id == int(user_id))
        if not_user_id is not None:
            sql = sql.where(Payment.user_id != not_user_id)
        if from_address is not None:
            sql = sql.where(Payment.from_address == str(from_address))
        if usdt_address is not None:
            sql = sql.where(Payment.usdt_address == str(usdt_address))
        if transaction_hash is not None:
            sql = sql.where(Payment.transaction_hash == str(transaction_hash))
        if status is not None:
            sql = sql.where(Payment.status == status)
        if amount_usdt is not None:
            sql = sql.where(Payment.amount_usdt == amount_usdt)
        if timestamp is not None:
            sql = sql.where(Payment.timestamp == timestamp)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(Payment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(Payment.added_at >= start_date)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def select_payments_amount_usdt(
        user_id = None,
        not_user_id = None,
        from_address = None,
        usdt_address = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        timestamp = None,
        added_at_date_type = None
):
    async with get_session() as session:
        sql = select(func.sum(Payment.amount_usdt))
        if user_id is not None:
            sql = sql.where(Payment.user_id == int(user_id))
        if not_user_id is not None:
            sql = sql.where(Payment.user_id != not_user_id)
        if from_address is not None:
            sql = sql.where(Payment.from_address == str(from_address))
        if usdt_address is not None:
            sql = sql.where(Payment.usdt_address == str(usdt_address))
        if transaction_hash is not None:
            sql = sql.where(Payment.transaction_hash == str(transaction_hash))
        if status is not None:
            sql = sql.where(Payment.status == status)
        if amount_usdt is not None:
            sql = sql.where(Payment.amount_usdt == amount_usdt)
        if timestamp is not None:
            sql = sql.where(Payment.timestamp == timestamp)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(Payment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(Payment.added_at >= start_date)
        result = await session.execute(sql)
        response = result.scalar()
        return response if response else 0


async def update_payment(
        primary_id = None,
        user_id = None,
        from_address = None,
        usdt_address = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        timestamp = None,
        added_at_date_type = None,
        data = None
    ):
    async with get_session() as session:
        sql = update(Payment)
        if primary_id is not None:
            sql = sql.where(Payment.id == int(primary_id))
        if user_id is not None:
            sql = sql.where(Payment.user_id == int(user_id))
        if from_address is not None:
            sql = sql.where(Payment.from_address == str(from_address))
        if usdt_address is not None:
            sql = sql.where(Payment.usdt_address == str(usdt_address))
        if transaction_hash is not None:
            sql = sql.where(Payment.transaction_hash == str(transaction_hash))
        if status is not None:
            sql = sql.where(Payment.status == status)
        if amount_usdt is not None:
            sql = sql.where(Payment.amount_usdt == amount_usdt)
        if timestamp is not None:
            sql = sql.where(Payment.timestamp == timestamp)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(Payment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(Payment.added_at >= start_date)
        await session.execute(sql.values(data))
        await session.commit()

