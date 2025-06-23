from typing import *
from datetime import datetime, timedelta
from datetime import time as dt_time
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import Group, PhoneQueue


async def add_group(
        group_id = None,
        group_name = None,
        group_link = None
    ):
    async with get_session() as session:
        sql = Group(
            group_id=group_id,
            group_name=group_name,
            group_link=group_link,
            created_at=datetime.now()
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_group(
        group_id = None,
        work_status = None,
        cross_timeout = None,
    ):
    async with get_session() as session:
        sql = select(Group).limit(1)
        if group_id is not None:
            sql = sql.where(Group.group_id == group_id)
        if work_status is not None:
            sql = sql.where(Group.work_status == work_status)
        if cross_timeout is not None:
            sql = sql.where(Group.cross_timeout == cross_timeout)
        result = await session.execute(sql)
        return result.scalar()


async def select_groups(
        group_id = None,
        work_status = None,
        cross_timeout = None,
        phone_queue_status = None,
):
    async with get_session() as session:
        if phone_queue_status:
            sql = select(
                Group,
                func.count(PhoneQueue.id).label('queue_count')
            ).outerjoin(
                PhoneQueue, PhoneQueue.group_id == Group.group_id
            ).group_by(
                Group.group_id
            ).order_by(
                func.count(PhoneQueue.id).desc()
            )
        else:
            sql = select(Group)
        if group_id is not None:
            sql = sql.where(Group.group_id == group_id)
        if work_status is not None:
            sql = sql.where(Group.work_status == work_status)
        if cross_timeout is not None:
            sql = sql.where(Group.cross_timeout == cross_timeout)
        if phone_queue_status:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(
                or_(
                    and_(PhoneQueue.buyed_at >= today_start, PhoneQueue.buyed_at <= today_end, PhoneQueue.status == 17),
                    and_(PhoneQueue.slet_at >= today_start, PhoneQueue.slet_at <= today_end, PhoneQueue.status == 18),
                )
            )
            
            # sql = sql.where(
            #     or_(
            #         PhoneQueue.status.in_([17, 18])
            #     )
            # )
            # today_start = datetime.combine(datetime.today(), dt_time.min)
            # today_end = datetime.combine(datetime.today(), dt_time.max)
            # sql = sql.where(PhoneQueue.updated_at >= today_start).where(PhoneQueue.updated_at <= today_end)

            # sql = sql.where(
            #     exists().where(
            #         PhoneQueue.group_id == Group.group_id,
            #         or_(PhoneQueue.status.in_([17, 18]))
            #     )
            # )
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_group(
        group_id = None,
        work_status = None,
        cross_timeout = None,
        data = None
    ):
    async with get_session() as session:
        sql = update(Group)
        if group_id is not None:
            sql = sql.where(Group.group_id == group_id)
        if work_status is not None:
            sql = sql.where(Group.work_status == work_status)
        if cross_timeout is not None:
            sql = sql.where(Group.cross_timeout == cross_timeout)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_group(
        group_id = None,
        work_status = None,
        cross_timeout = None,
    ):
    async with get_session() as session:
        sql = delete(Group)
        if group_id is not None:
            sql = sql.where(Group.group_id == group_id)
        if work_status is not None:
            sql = sql.where(Group.work_status == work_status)
        if cross_timeout is not None:
            sql = sql.where(Group.cross_timeout == cross_timeout)
        await session.execute(sql)
        await session.commit()

