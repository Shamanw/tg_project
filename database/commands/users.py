from typing import *
from datetime import datetime, timedelta
from datetime import time as dt_time
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import User, PhoneQueue


async def add_user(
        user_id = None,
        fullname = None,
        username = None
    ):
    async with get_session() as session:
        sql = User(
            user_id=user_id,
            fullname=fullname,
            username=username,
            registered_at=datetime.now()
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_user(
        primary_id = None,
        user_id = None,
        referrer_id = None,
        user_hash = None,
        role = None,
        is_banned = None,
        added_count = None,
        calc_amount = None,
    ):
    async with get_session() as session:
        sql = select(User).limit(1)
        if primary_id is not None:
            sql = sql.where(User.id == primary_id)
        if user_id is not None:
            sql = sql.where(User.user_id == user_id)
        if referrer_id is not None:
            sql = sql.where(User.referrer_id == referrer_id)
        if user_hash is not None:
            sql = sql.where(User.user_hash == user_hash)
        if role is not None:
            sql = sql.where(User.role == role)
        if is_banned is not None:
            sql = sql.where(User.is_banned == is_banned)
        if added_count is not None:
            sql = sql.where(User.added_count == added_count)
        if calc_amount is not None:
            sql = sql.where(User.calc_amount == calc_amount)
        result = await session.execute(sql)
        return result.scalar()


async def select_users(
        without_user_id = None,
        user_id = None,
        referrer_id = None,
        user_hash = None,
        role = None,
        not_role = None,
        is_banned = None,
        added_count = None,
        calc_amount = None,
        phone_queue_status = None,
):
    async with get_session() as session:
        if phone_queue_status:
            sql = select(
                User,
                func.count(PhoneQueue.id).label('drop_count')
            ).outerjoin(
                PhoneQueue, PhoneQueue.drop_id == User.user_id
            ).group_by(
                User.user_id
            ).order_by(
                func.count(PhoneQueue.id).desc()  # сортировка по количеству записей
            )
        else:
            sql = select(User)
        if without_user_id is not None:
            sql = sql.where(User.user_id != int(without_user_id))
        if user_id is not None:
            sql = sql.where(User.user_id == user_id)
        if referrer_id is not None:
            sql = sql.where(User.referrer_id == referrer_id)
        if user_hash is not None:
            sql = sql.where(User.user_hash == user_hash)
        if role is not None:
            sql = sql.where(User.role == role)
        if not_role is not None:
            sql = sql.where(User.role != not_role)
        if is_banned is not None:
            sql = sql.where(User.is_banned == is_banned)
        if added_count is not None:
            sql = sql.where(User.added_count == added_count)
        if calc_amount is not None:
            sql = sql.where(User.calc_amount == calc_amount)
        if phone_queue_status:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(
                or_(
                    and_(PhoneQueue.set_at >= today_start, PhoneQueue.set_at <= today_end),
                    and_(PhoneQueue.buyed_at >= today_start, PhoneQueue.buyed_at <= today_end, PhoneQueue.status == 17),
                    and_(PhoneQueue.slet_at >= today_start, PhoneQueue.slet_at <= today_end, PhoneQueue.status == 18),
                    and_(PhoneQueue.deleted_at >= today_start, PhoneQueue.deleted_at <= today_end, PhoneQueue.status == 21),
                    and_(PhoneQueue.slet_at >= today_start, PhoneQueue.slet_at <= today_end, PhoneQueue.status == 24)
                )
            )
            # sql = sql.where(
            #     or_(
            #         PhoneQueue.status.in_([17, 18]),
            #         PhoneQueue.withdraw_status == 1,
            #         PhoneQueue.confirmed_status == 1
            #     )
            # )
            # today_start = datetime.combine(datetime.today(), dt_time.min)
            # today_end = datetime.combine(datetime.today(), dt_time.max)
            # sql = sql.where(PhoneQueue.updated_at >= today_start).where(PhoneQueue.updated_at <= today_end)

        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def select_inactive_drops(days):
    async with get_session() as session:
        target_date = datetime.now() - timedelta(days=days)

        subquery = (
            select(PhoneQueue.drop_id, func.count(PhoneQueue.id).label('record_count'))
            .where(
                and_(
                    PhoneQueue.drop_id == User.user_id,
                    PhoneQueue.set_at.isnot(None),
                    PhoneQueue.set_at >= target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                )
            )
            .group_by(PhoneQueue.drop_id)
            .subquery()
        )
        sql = (
            select(User)
            .outerjoin(subquery, User.user_id == subquery.c.drop_id)
            .where(
                and_(
                    User.role == 'drop',
                    or_(
                        subquery.c.record_count.is_(None),
                        subquery.c.record_count < 5
                    )
                )
            )
        )
        result = await session.execute(sql)
        users = result.scalars().all()
        return users


async def select_inactive_drops_without_success(days=2):
    async with get_session() as session:
        registration_date = datetime.now() - timedelta(days=days)
        query = (
            select(User)
            .where(
                and_(
                    User.role == 'drop',
                    User.registered_at <= registration_date,
                    ~exists(
                        select(1)
                        .where(
                            and_(
                                PhoneQueue.drop_id == User.user_id,
                                PhoneQueue.set_at.isnot(None)
                            )
                        )
                    )
                )
            )
        )
        result = await session.execute(query)
        return result.scalars().all()


async def select_inactive_drops_full(days=5, days_registration=None):
    async with get_session() as session:
        target_date = datetime.now() - timedelta(days=days)
        activity_subquery = (
            select(PhoneQueue.drop_id, func.count(PhoneQueue.id).label('record_count'))
            .where(
                and_(
                    PhoneQueue.set_at.isnot(None),
                    PhoneQueue.set_at >= target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                )
            )
            .group_by(PhoneQueue.drop_id)
            .subquery()
        )
        conditions = [
            User.role == 'drop',
            or_(
                activity_subquery.c.record_count.is_(None),
                activity_subquery.c.record_count < 5
            )
        ]
        if days_registration is not None:
            registration_date = datetime.now() - timedelta(days=days_registration)
            conditions.append(User.registered_at <= registration_date)
            no_success_condition = ~exists(
                select(1).where(
                    and_(
                        PhoneQueue.drop_id == User.user_id,
                        PhoneQueue.set_at.isnot(None)
                    )
                )
            )
            conditions.append(no_success_condition)
        query = (
            select(User)
            .outerjoin(activity_subquery, User.user_id == activity_subquery.c.drop_id)
            .where(and_(*conditions))
        )
        result = await session.execute(query)
        return result.scalars().all()









async def update_user(
        primary_id = None,
        user_id = None,
        referrer_id = None,
        user_hash = None,
        role = None,
        is_banned = None,
        added_count = None,
        calc_amount = None,
        data = None
    ):
    async with get_session() as session:
        sql = update(User)
        if primary_id is not None:
            sql = sql.where(User.id == primary_id)
        if user_id is not None:
            sql = sql.where(User.user_id == user_id)
        if referrer_id is not None:
            sql = sql.where(User.referrer_id == referrer_id)
        if user_hash is not None:
            sql = sql.where(User.user_hash == user_hash)
        if role is not None:
            sql = sql.where(User.role == role)
        if is_banned is not None:
            sql = sql.where(User.is_banned == is_banned)
        if added_count is not None:
            sql = sql.where(User.added_count == added_count)
        if calc_amount is not None:
            sql = sql.where(User.calc_amount == calc_amount)
        await session.execute(sql.values(data))
        await session.commit()

