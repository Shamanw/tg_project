from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import CryptoBotPayment


async def add_cryptobot_payment(
        user_id = None,
        invoice_id = None,
        transaction_hash = None,
        amount_usdt = None,
        invoice_type = 0,
    ):
    async with get_session() as session:
        sql = CryptoBotPayment(
            user_id=user_id,
            invoice_id=invoice_id,
            transaction_hash=transaction_hash,
            amount_usdt=amount_usdt,
            invoice_type=invoice_type,
            added_at=datetime.now(),
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_cryptobot_payment(
        primary_id = None,
        user_id = None,
        invoice_id = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        added_at_date_type = None
    ):
    async with get_session() as session:
        sql = select(CryptoBotPayment).limit(1)
        if primary_id is not None:
            sql = sql.where(CryptoBotPayment.id == int(primary_id))
        if user_id is not None:
            sql = sql.where(CryptoBotPayment.user_id == int(user_id))
        if invoice_id is not None:
            sql = sql.where(CryptoBotPayment.invoice_id == int(invoice_id))
        if transaction_hash is not None:
            sql = sql.where(CryptoBotPayment.transaction_hash == transaction_hash)
        if status is not None:
            sql = sql.where(CryptoBotPayment.status == status)
        if amount_usdt is not None:
            sql = sql.where(CryptoBotPayment.amount_usdt == amount_usdt)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(CryptoBotPayment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(CryptoBotPayment.added_at >= start_date)
        result = await session.execute(sql)
        return result.scalar()


async def select_cryptobot_payments(
        user_id = None,
        invoice_id = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        added_at_date_type = None
):
    async with get_session() as session:
        sql = select(CryptoBotPayment)
        if user_id is not None:
            sql = sql.where(CryptoBotPayment.user_id == int(user_id))
        if invoice_id is not None:
            sql = sql.where(CryptoBotPayment.invoice_id == int(invoice_id))
        if transaction_hash is not None:
            sql = sql.where(CryptoBotPayment.transaction_hash == transaction_hash)
        if status is not None:
            sql = sql.where(CryptoBotPayment.status == status)
        if amount_usdt is not None:
            sql = sql.where(CryptoBotPayment.amount_usdt == amount_usdt)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(CryptoBotPayment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(CryptoBotPayment.added_at >= start_date)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def select_cryptobot_payments_amount_usdt(
        user_id = None,
        invoice_id = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        added_at_date_type = None
):
    async with get_session() as session:
        sql = select(func.sum(CryptoBotPayment.amount_usdt))
        if user_id is not None:
            sql = sql.where(CryptoBotPayment.user_id == int(user_id))
        if invoice_id is not None:
            sql = sql.where(CryptoBotPayment.invoice_id == int(invoice_id))
        if transaction_hash is not None:
            sql = sql.where(CryptoBotPayment.transaction_hash == transaction_hash)
        if status is not None:
            sql = sql.where(CryptoBotPayment.status == status)
        if amount_usdt is not None:
            sql = sql.where(CryptoBotPayment.amount_usdt == amount_usdt)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(CryptoBotPayment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(CryptoBotPayment.added_at >= start_date)
        result = await session.execute(sql)
        response = result.scalar()
        return response if response else 0


async def update_cryptobot_payment(
        primary_id = None,
        user_id = None,
        invoice_id = None,
        transaction_hash = None,
        status = None,
        amount_usdt = None,
        added_at_date_type = None,
        data = None
    ):
    async with get_session() as session:
        sql = update(CryptoBotPayment)
        if primary_id is not None:
            sql = sql.where(CryptoBotPayment.id == int(primary_id))
        if user_id is not None:
            sql = sql.where(CryptoBotPayment.user_id == int(user_id))
        if invoice_id is not None:
            sql = sql.where(CryptoBotPayment.invoice_id == int(invoice_id))
        if transaction_hash is not None:
            sql = sql.where(CryptoBotPayment.transaction_hash == transaction_hash)
        if status is not None:
            sql = sql.where(CryptoBotPayment.status == status)
        if amount_usdt is not None:
            sql = sql.where(CryptoBotPayment.amount_usdt == amount_usdt)
        if added_at_date_type is not None:
            now = datetime.now()
            start_date = None
            if added_at_date_type == 'day':
                start_date = datetime(now.year, now.month, now.day)
            elif added_at_date_type == 'yesterday':
                start_date = datetime(now.year, now.month, now.day) - timedelta(days=1)
                sql = sql.where(CryptoBotPayment.added_at < start_date + timedelta(days=1))
            elif added_at_date_type == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
            elif added_at_date_type == 'month':
                start_date = datetime(now.year, now.month, 1)
            if start_date:
                sql = sql.where(CryptoBotPayment.added_at >= start_date)
        await session.execute(sql.values(data))
        await session.commit()

