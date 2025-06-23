import time

from typing import *
from datetime import datetime, timedelta
from datetime import time as dt_time
from collections import defaultdict

from sqlalchemy import *
from sqlalchemy.sql import over
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import PhoneQueue, User, OtlegaGroupBase, OtlegaGroup


async def add_phone_queue(
        drop_id = None,
        phone_number = None,
    ):
    async with get_session() as session:
        sql = PhoneQueue(
            drop_id=drop_id,
            phone_number=phone_number,
            added_at=datetime.now(),
            updated_at=datetime.now(),
            last_check_at=datetime.now(),
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql

async def select_phone_queue(
        primary_id = None,
        is_none_otlega_unique_id = None,
        drop_id = None,
        client_id = None,
        group_id = None,
        phone_number = None,
        session_name = None,
        confirmed_status = None,
        status = None,
        auth_proxy = None,
        statuses = None,
        group_bot_message_id = None,
        group_user_message_id = None,
        drop_bot_message_id = None,
        drop_user_message_id = None,
        waiting_confirm_status = None,
        withdraw_status = None,
        pre_withdraw_statuses = None,
        cryptobot_admin_notify = None,
        sent_sms_status = None,
        skip_count = None,
        skip_group_id_1 = None,
        skip_group_id_2 = None,
        not_skip_group_id_1 = None,
        not_skip_group_id_2 = None,
        random_status = None,
        sort_asc = None,
        sort_desc = None,
        sort_one = None,
        drop_sort = None,
    ):
    async with get_session() as session:
        if random_status:
            sql = select(PhoneQueue)
        elif sort_one or drop_sort:
            sql = select(PhoneQueue)
        else:
            sql = select(PhoneQueue).limit(1)
        if primary_id is not None:
            sql = sql.where(PhoneQueue.id == primary_id)
        if is_none_otlega_unique_id is not None:
            sql = sql.where(PhoneQueue.otlega_unique_id.is_(None))
        if drop_id is not None:
            sql = sql.where(PhoneQueue.drop_id == drop_id)
        if client_id is not None:
            sql = sql.where(PhoneQueue.client_id == client_id)
        if group_id is not None:
            sql = sql.where(PhoneQueue.group_id == group_id)
        if phone_number is not None:
            sql = sql.where(PhoneQueue.phone_number == phone_number)
        if session_name is not None:
            sql = sql.where(PhoneQueue.session_name == session_name)
        if confirmed_status is not None:
            sql = sql.where(PhoneQueue.confirmed_status == confirmed_status)
        if status is not None:
            sql = sql.where(PhoneQueue.status == status)
        if auth_proxy is not None:
            sql = sql.where(PhoneQueue.auth_proxy == auth_proxy)
        if statuses is not None:
            conditions = [PhoneQueue.status == status for status in statuses]
            sql = sql.where(or_(*conditions))
        if group_bot_message_id is not None:
            sql = sql.where(PhoneQueue.group_bot_message_id == group_bot_message_id)
        if group_user_message_id is not None:
            sql = sql.where(PhoneQueue.group_user_message_id == group_user_message_id)
        if drop_bot_message_id is not None:
            sql = sql.where(PhoneQueue.drop_bot_message_id == drop_bot_message_id)
        if drop_user_message_id is not None:
            sql = sql.where(PhoneQueue.drop_user_message_id == drop_user_message_id)
        if waiting_confirm_status is not None:
            sql = sql.where(PhoneQueue.waiting_confirm_status == waiting_confirm_status)
        if withdraw_status is not None:
            sql = sql.where(PhoneQueue.withdraw_status == withdraw_status)
        if pre_withdraw_statuses is not None:
            conditions = [PhoneQueue.pre_withdraw_status == pre_withdraw_status for pre_withdraw_status in pre_withdraw_statuses]
        if cryptobot_admin_notify is not None:
            sql = sql.where(PhoneQueue.cryptobot_admin_notify == cryptobot_admin_notify)
        if sent_sms_status is not None:
            sql = sql.where(PhoneQueue.sent_sms_status == sent_sms_status)
        if skip_count is not None:
            sql = sql.where(PhoneQueue.skip_count == skip_count)
        if skip_group_id_1 is not None:
            sql = sql.where(PhoneQueue.skip_group_id_1 == skip_group_id_1)
        if skip_group_id_2 is not None:
            sql = sql.where(PhoneQueue.skip_group_id_2 == skip_group_id_2)
        if not_skip_group_id_1 is not None:
            sql = sql.where(or_(PhoneQueue.skip_group_id_1 != not_skip_group_id_1, PhoneQueue.skip_group_id_1.is_(None)))
        if not_skip_group_id_2 is not None:
            sql = sql.where(or_(PhoneQueue.skip_group_id_2 != not_skip_group_id_2, PhoneQueue.skip_group_id_2.is_(None)))
        if random_status:
            sql = sql.order_by(func.random()).limit(1)
        elif sort_asc:
            sql = sql.order_by(PhoneQueue.added_at.asc())
        elif sort_desc:
            sql = sql.order_by(PhoneQueue.added_at.desc())
        else:
            result = await session.execute(sql)
            return result.scalar()


async def select_phone_queues(
        alive_status_not_in = None,
        alive_status_in = None,
        alive_status = None,
        alive_last_check_status = None,
        alive_hold_status = None,
        pslet_status = None,
        referrer_amount_is_not_none = None,
        client_bot = None,
        otlega_count_days = None,
        otlega_unique_id = None,
        is_none_otlega_unique_id = None,
        otlega_unique_id_is_none = None,
        drop_id = None,
        client_id = None,
        group_id = None,
        phone_number = None,
        session_name = None,
        confirmed_status = None,
        status = None,
        auth_proxy = None,
        statuses = None,
        group_bot_message_id = None,
        group_user_message_id = None,
        drop_bot_message_id = None,
        drop_user_message_id = None,
        waiting_confirm_status = None,
        withdraw_status = None,
        pre_withdraw_statuses = None,
        cryptobot_admin_notify = None,
        sent_sms_status = None,
        added_at_00_00 = None,
        updated_at_00_00 = None,
        added_at_yesterday = None,
        updated_at_yesterday = None,
        added_at_week = None,
        updated_at_week = None,
        added_at_month = None,
        updated_at_month = None,
        added_at_previous_month = None,
        updated_at_previous_month = None,
        withdraw_at_00_00 = None,
        set_at_00_00 = None,
        withdraw_at_yesterday = None,
        set_at_yesterday = None,
        withdraw_at_week = None,
        set_at_week = None,
        withdraw_at_month = None,
        set_at_month = None,
        withdraw_at_previous_month = None,
        set_at_previous_month = None,
        confirmed_at_00_00 = None,
        slet_at_00_00 = None,
        slet_last_at_00_00 = None,
        slet_main_at_00_00 = None,
        deleted_at_00_00 = None,
        buyed_at_00_00 = None,
        unlocked_at_00_00 = None,
        confirmed_at_yesterday = None,
        slet_at_yesterday = None,
        slet_last_at_yesterday = None,
        slet_main_at_yesterday = None,
        deleted_at_yesterday = None,
        buyed_at_yesterday = None,
        unlocked_at_yesterday = None,
        confirmed_at_week = None,
        slet_at_week = None,
        slet_last_at_week = None,
        slet_main_at_week = None,
        deleted_at_week = None,
        buyed_at_week = None,
        unlocked_at_week = None,
        confirmed_at_month = None,
        slet_at_month = None,
        slet_last_at_month = None,
        slet_main_at_month = None,
        deleted_at_month = None,
        buyed_at_month = None,
        unlocked_at_month = None,
        confirmed_at_previous_month = None,
        slet_at_previous_month = None,
        slet_last_at_previous_month = None,
        slet_main_at_previous_month = None,
        deleted_at_previous_month = None,
        buyed_at_previous_month = None,
        unlocked_at_previous_month = None,
        skip_count = None,
        skip_group_id_1 = None,
        skip_group_id_2 = None,
        not_skip_group_id_1 = None,
        not_skip_group_id_2 = None,
        sort_asc = None,
        sort_desc = None,
        not_payed_amount = None,
        payed_amount_total = None,
        not_buyed_amount = None,
        buyed_amount_total = None,
        not_unlocked_amount = None,
        unlocked_amount_total = None,
        referrer_amount_total = None,
        count = None,
        referrer_id = None,
        unban_month_status = None,
        slet_at_is_none = None,
        slet_at_is_not_none = None,
        slet_last_at_is_none = None,
        slet_last_at_is_not_none = None,
):
    async with get_session() as session:
        if count:
            sql = select(func.count()).select_from(PhoneQueue)
        elif payed_amount_total:
            sql = select(func.sum(PhoneQueue.payed_amount))
        elif buyed_amount_total:
            sql = select(func.sum(PhoneQueue.buyed_amount))
        elif unlocked_amount_total:
            sql = select(func.sum(PhoneQueue.unlocked_amount))
        elif referrer_amount_total:
            sql = select(func.sum(PhoneQueue.referrer_amount))
        else:
            sql = select(PhoneQueue)
            
        if slet_at_is_none is not None:
            sql = sql.where(PhoneQueue.slet_at.is_(None))
        if slet_at_is_not_none:
            sql = sql.where(PhoneQueue.slet_at.isnot(None))
        if slet_last_at_is_none is not None:
            sql = sql.where(PhoneQueue.slet_last_at.is_(None))
        if slet_last_at_is_not_none:
            sql = sql.where(PhoneQueue.slet_last_at.isnot(None))

        if alive_status_in is not None:
            conditions = [PhoneQueue.alive_status == alive_status for alive_status in alive_status_in]
            sql = sql.where(or_(*conditions))
        if alive_status_not_in is not None:
            conditions = [PhoneQueue.alive_status != alive_status for alive_status in alive_status_not_in]
            sql = sql.where(and_(*conditions))
        if alive_status is not None:
            sql = sql.where(PhoneQueue.alive_status == alive_status)
        if alive_last_check_status is not None:
            sql = sql.where(PhoneQueue.alive_last_check_status == alive_last_check_status)
        if alive_hold_status is not None:
            sql = sql.where(PhoneQueue.alive_hold_status == alive_hold_status)
        if unban_month_status is not None:
            sql = sql.where(PhoneQueue.unban_month_status == unban_month_status)
        if pslet_status is not None:
            sql = sql.where(PhoneQueue.pslet_status == pslet_status)
        if referrer_amount_is_not_none:
            sql = sql.where(PhoneQueue.referrer_amount.isnot(None))
        if referrer_id is not None:
            sql = sql.where(PhoneQueue.referrer_id == referrer_id)
        if client_bot is not None:
            sql = sql.where(PhoneQueue.client_bot == client_bot)
        if otlega_count_days is not None:
            sql = sql.where(PhoneQueue.otlega_count_days == otlega_count_days)
        if otlega_unique_id is not None:
            sql = sql.where(PhoneQueue.otlega_unique_id == otlega_unique_id)
        if is_none_otlega_unique_id is not None or otlega_unique_id_is_none is not None:
            sql = sql.where(PhoneQueue.otlega_unique_id.is_(None))
        if drop_id is not None:
            sql = sql.where(PhoneQueue.drop_id == drop_id)
        if client_id is not None:
            sql = sql.where(PhoneQueue.client_id == client_id)
        if group_id is not None:
            sql = sql.where(PhoneQueue.group_id == group_id)
        if phone_number is not None:
            sql = sql.where(PhoneQueue.phone_number == phone_number)
        if session_name is not None:
            sql = sql.where(PhoneQueue.session_name == session_name)
        if confirmed_status is not None:
            sql = sql.where(PhoneQueue.confirmed_status == confirmed_status)
        if status is not None:
            sql = sql.where(PhoneQueue.status == status)
        if auth_proxy is not None:
            sql = sql.where(PhoneQueue.auth_proxy == auth_proxy)
        if statuses is not None:
            conditions = [PhoneQueue.status == status for status in statuses]
            sql = sql.where(or_(*conditions))
        if group_bot_message_id is not None:
            sql = sql.where(PhoneQueue.group_bot_message_id == group_bot_message_id)
        if group_user_message_id is not None:
            sql = sql.where(PhoneQueue.group_user_message_id == group_user_message_id)
        if drop_bot_message_id is not None:
            sql = sql.where(PhoneQueue.drop_bot_message_id == drop_bot_message_id)
        if drop_user_message_id is not None:
            sql = sql.where(PhoneQueue.drop_user_message_id == drop_user_message_id)
        if waiting_confirm_status is not None:
            sql = sql.where(PhoneQueue.waiting_confirm_status == waiting_confirm_status)
        if withdraw_status is not None:
            sql = sql.where(PhoneQueue.withdraw_status == withdraw_status)
        if pre_withdraw_statuses is not None:
            conditions = [PhoneQueue.pre_withdraw_status == pre_withdraw_status for pre_withdraw_status in pre_withdraw_statuses]
            sql = sql.where(or_(*conditions))
        if cryptobot_admin_notify is not None:
            sql = sql.where(PhoneQueue.cryptobot_admin_notify == cryptobot_admin_notify)
        if sent_sms_status is not None:
            sql = sql.where(PhoneQueue.sent_sms_status == sent_sms_status)

        if added_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.added_at >= today_start).where(PhoneQueue.added_at <= today_end)
        if updated_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.updated_at >= today_start).where(PhoneQueue.updated_at <= today_end)

        if added_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.added_at >= yesterday_start).where(PhoneQueue.added_at <= yesterday_end)
        if updated_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.updated_at >= yesterday_start).where(PhoneQueue.updated_at <= yesterday_end)

        if added_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.added_at >= week_start).where(PhoneQueue.added_at <= week_end)
        if updated_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.updated_at >= week_start).where(PhoneQueue.updated_at <= week_end)

        if added_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.added_at >= month_start).where(PhoneQueue.added_at <= month_end)
        if updated_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.updated_at >= month_start).where(PhoneQueue.updated_at <= month_end)

        if added_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.added_at >= month_start).where(PhoneQueue.added_at <= month_end)
        if updated_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.updated_at >= month_start).where(PhoneQueue.updated_at <= month_end)


        if withdraw_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.withdraw_at >= today_start).where(PhoneQueue.withdraw_at <= today_end)
        if set_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.set_at >= today_start).where(PhoneQueue.set_at <= today_end)

        if withdraw_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.withdraw_at >= yesterday_start).where(PhoneQueue.withdraw_at <= yesterday_end)
        if set_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.set_at >= yesterday_start).where(PhoneQueue.set_at <= yesterday_end)

        if withdraw_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.withdraw_at >= week_start).where(PhoneQueue.withdraw_at <= week_end)
        if set_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.set_at >= week_start).where(PhoneQueue.set_at <= week_end)

        if withdraw_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.withdraw_at >= month_start).where(PhoneQueue.withdraw_at <= month_end)
        if set_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.set_at >= month_start).where(PhoneQueue.set_at <= month_end)

        if withdraw_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.withdraw_at >= month_start).where(PhoneQueue.withdraw_at <= month_end)
        if set_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.set_at >= month_start).where(PhoneQueue.set_at <= month_end)


        if confirmed_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.confirmed_at >= today_start).where(PhoneQueue.confirmed_at <= today_end)
        if slet_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_at >= today_start).where(PhoneQueue.slet_at <= today_end)
        if slet_last_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_last_at >= today_start).where(PhoneQueue.slet_last_at <= today_end)
        if slet_main_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_main_at >= today_start).where(PhoneQueue.slet_main_at <= today_end)
        if deleted_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.deleted_at >= today_start).where(PhoneQueue.deleted_at <= today_end)
        if buyed_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.buyed_at >= today_start).where(PhoneQueue.buyed_at <= today_end)
        if unlocked_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.unlocked_at >= today_start).where(PhoneQueue.unlocked_at <= today_end)

        if confirmed_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.confirmed_at >= yesterday_start).where(PhoneQueue.confirmed_at <= yesterday_end)
        if slet_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_at >= yesterday_start).where(PhoneQueue.slet_at <= yesterday_end)
        if slet_last_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_last_at >= yesterday_start).where(PhoneQueue.slet_last_at <= yesterday_end)
        if slet_main_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_main_at >= yesterday_start).where(PhoneQueue.slet_main_at <= yesterday_end)
        if deleted_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.deleted_at >= yesterday_start).where(PhoneQueue.deleted_at <= yesterday_end)
        if buyed_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.buyed_at >= yesterday_start).where(PhoneQueue.buyed_at <= yesterday_end)
        if unlocked_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.unlocked_at >= yesterday_start).where(PhoneQueue.unlocked_at <= yesterday_end)

        if confirmed_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.confirmed_at >= week_start).where(PhoneQueue.confirmed_at <= week_end)
        if slet_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.slet_at >= week_start).where(PhoneQueue.slet_at <= week_end)
        if slet_last_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.slet_last_at >= week_start).where(PhoneQueue.slet_last_at <= week_end)
        if slet_main_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.slet_main_at >= week_start).where(PhoneQueue.slet_main_at <= week_end)
        if deleted_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.deleted_at >= week_start).where(PhoneQueue.deleted_at <= week_end)
        if buyed_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.buyed_at >= week_start).where(PhoneQueue.buyed_at <= week_end)
        if unlocked_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.unlocked_at >= week_start).where(PhoneQueue.unlocked_at <= week_end)

        if confirmed_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.confirmed_at >= month_start).where(PhoneQueue.confirmed_at <= month_end)
        if slet_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.slet_at >= month_start).where(PhoneQueue.slet_at <= month_end)
        if slet_last_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.slet_last_at >= month_start).where(PhoneQueue.slet_last_at <= month_end)
        if slet_main_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.slet_main_at >= month_start).where(PhoneQueue.slet_main_at <= month_end)
        if buyed_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.buyed_at >= month_start).where(PhoneQueue.buyed_at <= month_end)
        if unlocked_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.unlocked_at >= month_start).where(PhoneQueue.unlocked_at <= month_end)

        if confirmed_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.confirmed_at >= month_start).where(PhoneQueue.confirmed_at <= month_end)
        if slet_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_at >= month_start).where(PhoneQueue.slet_at <= month_end)
        if slet_last_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_last_at >= month_start).where(PhoneQueue.slet_last_at <= month_end)
        if slet_main_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.slet_main_at >= month_start).where(PhoneQueue.slet_main_at <= month_end)
        if buyed_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.buyed_at >= month_start).where(PhoneQueue.buyed_at <= month_end)
        if unlocked_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.unlocked_at >= month_start).where(PhoneQueue.unlocked_at <= month_end)

        if deleted_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(PhoneQueue.deleted_at >= today_start).where(PhoneQueue.deleted_at <= today_end)
        if deleted_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(PhoneQueue.deleted_at >= yesterday_start).where(PhoneQueue.deleted_at <= yesterday_end)
        if deleted_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(PhoneQueue.deleted_at >= week_start).where(PhoneQueue.deleted_at <= week_end)
        if deleted_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(PhoneQueue.deleted_at >= month_start).where(PhoneQueue.deleted_at <= month_end)
        if deleted_at_previous_month:
            today = datetime.today()
            first_day_current_month = today.replace(day=1)
            last_day_prev_month = first_day_current_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            month_start = datetime.combine(first_day_prev_month.date(), dt_time.min)
            month_end = datetime.combine(last_day_prev_month.date(), dt_time.max)
            sql = sql.where(PhoneQueue.deleted_at >= month_start).where(PhoneQueue.deleted_at <= month_end)
 
 

        if skip_count is not None:
            sql = sql.where(PhoneQueue.skip_count == skip_count)
        if skip_group_id_1 is not None:
            sql = sql.where(PhoneQueue.skip_group_id_1 == skip_group_id_1)
        if skip_group_id_2 is not None:
            sql = sql.where(PhoneQueue.skip_group_id_2 == skip_group_id_2)
        if not_skip_group_id_1 is not None:
            sql = sql.where(or_(PhoneQueue.skip_group_id_1 != not_skip_group_id_1, PhoneQueue.skip_group_id_1.is_(None)))
        if not_skip_group_id_2 is not None:
            sql = sql.where(or_(PhoneQueue.skip_group_id_2 != not_skip_group_id_2, PhoneQueue.skip_group_id_2.is_(None)))
        
        if not_payed_amount:
            sql = sql.where(PhoneQueue.payed_amount != None, PhoneQueue.payed_amount > 0)

        if payed_amount_total:
            sql = sql.where(PhoneQueue.payed_amount != None, PhoneQueue.payed_amount > 0)
            sum_result = await session.execute(sql)
            total_payed_amount = sum_result.scalar()
            if total_payed_amount is None or total_payed_amount <= 0:
                return 0
            else:
                return total_payed_amount

        if not_buyed_amount:
            sql = sql.where(PhoneQueue.buyed_amount != None, PhoneQueue.buyed_amount > 0)
        if not_unlocked_amount:
            sql = sql.where(PhoneQueue.unlocked_amount != None, PhoneQueue.unlocked_amount > 0)

        if buyed_amount_total:
            sql = sql.where(PhoneQueue.buyed_amount != None, PhoneQueue.buyed_amount > 0)
            sum_result = await session.execute(sql)
            total_buyed_amount = sum_result.scalar()
            if total_buyed_amount is None or total_buyed_amount <= 0:
                return 0
            else:
                return total_buyed_amount

        if unlocked_amount_total:
            sql = sql.where(PhoneQueue.unlocked_amount != None, PhoneQueue.unlocked_amount > 0)
            sum_result = await session.execute(sql)
            total_unlocked_amount = sum_result.scalar()
            if total_unlocked_amount is None or total_unlocked_amount <= 0:
                return 0
            else:
                return total_unlocked_amount

        if referrer_amount_total:
            sql = sql.where(PhoneQueue.referrer_amount != None, PhoneQueue.referrer_amount > 0)
            sum_result = await session.execute(sql)
            total_referrer_amount = sum_result.scalar()
            if total_referrer_amount is None or total_referrer_amount <= 0:
                return 0
            else:
                return total_referrer_amount

        if count:
            result = await session.execute(sql)
            return result.scalar()
        else:
            if sort_asc:
                sql = sql.order_by(PhoneQueue.added_at.asc())
            if sort_desc:
                sql = sql.order_by(PhoneQueue.added_at.desc())
            result = await session.execute(sql)
            results = result.scalars().all()
            return results


async def select_ready_session(group_id):
    async with get_session() as session:
        sql = (
            select(PhoneQueue)
            .where(PhoneQueue.status == 12)
            .where(PhoneQueue.client_bot == 0)
        )
        otlega_subquery = (
            select(OtlegaGroupBase.unique_id)
            .where(OtlegaGroupBase.group_id == group_id)
        )
        result = await session.execute(otlega_subquery)
        otlega_records = result.scalars().all()
        if not otlega_records:
            return None
        conditions = []
        default_condition = None
        for otlega_record in otlega_records:
            if otlega_record == 111:
                default_condition = PhoneQueue.otlega_unique_id.is_(None)
                continue
            days_condition = (
                select(OtlegaGroup.count_days)
                .where(OtlegaGroup.unique_id == otlega_record)
                .scalar_subquery()
            )
            conditions.append(
                and_(
                    PhoneQueue.otlega_unique_id == otlega_record,
                    (func.julianday(func.datetime('now')) - func.julianday(PhoneQueue.set_at)) > days_condition
                )
            )
        if default_condition is not None:
            conditions.append(default_condition)
        sql = sql.where(or_(*conditions)).order_by(PhoneQueue.set_at.desc())
        result = await session.execute(sql)
        return result.scalar()


async def select_ready_session(group_id):
    async with get_session() as session:
        sql = (
            select(PhoneQueue)
            .where(PhoneQueue.status == 12)
            .where(PhoneQueue.client_bot == 0)
        )
        otlega_subquery = (
            select(OtlegaGroupBase.unique_id)
            .where(OtlegaGroupBase.group_id == group_id)
        )
        result = await session.execute(otlega_subquery)
        otlega_records = result.scalars().all()
        if not otlega_records:
            return None
        conditions = []
        default_condition = None
        for otlega_record in otlega_records:
            if otlega_record == 111:
                default_condition = PhoneQueue.otlega_unique_id.is_(None)
                continue
            days_condition = (
                select(OtlegaGroup.count_days)
                .where(OtlegaGroup.unique_id == otlega_record)
                .scalar_subquery()
            )
            conditions.append(
                and_(
                    PhoneQueue.otlega_unique_id == otlega_record,
                    (func.julianday(func.datetime('now')) - func.julianday(PhoneQueue.set_at)) > days_condition
                )
            )
        if default_condition is not None:
            conditions.append(default_condition)
        sql = sql.where(or_(*conditions)).order_by(PhoneQueue.set_at.desc())
        result = await session.execute(sql)
        return result.scalar()


async def select_drop_phones_queue_actives(drop_id = None):
    async with get_session() as session:
        sql = select(PhoneQueue)
        sql = select(PhoneQueue).where(
            PhoneQueue.status.in_([4, 5, 6, 7]),
            # PhoneQueue.drop_id == drop_id,
            PhoneQueue.confirmed_at.is_not(None),
            PhoneQueue.slet_at.is_not(None)
        )
        if drop_id is not None:
            sql = sql.where(PhoneQueue.drop_id == drop_id)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_phone_queue(
        primary_id = None,
        drop_id = None,
        client_id = None,
        group_id = None,
        phone_number = None,
        session_name = None,
        confirmed_status = None,
        status = None,
        auth_proxy = None,
        statuses = None,
        group_bot_message_id = None,
        group_user_message_id = None,
        drop_bot_message_id = None,
        drop_user_message_id = None,
        waiting_confirm_status = None,
        withdraw_status = None,
        pre_withdraw_statuses = None,
        cryptobot_admin_notify = None,
        sent_sms_status = None,
        skip_count = None,
        skip_group_id_1 = None,
        skip_group_id_2 = None,
        not_skip_group_id_1 = None,
        not_skip_group_id_2 = None,
        sort_asc = None,
        sort_desc = None,
        data = None
    ):
    async with get_session() as session:
        sql = update(PhoneQueue)
        if primary_id is not None:
            sql = sql.where(PhoneQueue.id == primary_id)
        if drop_id is not None:
            sql = sql.where(PhoneQueue.drop_id == drop_id)
        if client_id is not None:
            sql = sql.where(PhoneQueue.client_id == client_id)
        if group_id is not None:
            sql = sql.where(PhoneQueue.group_id == group_id)
        if phone_number is not None:
            sql = sql.where(PhoneQueue.phone_number == phone_number)
        if session_name is not None:
            sql = sql.where(PhoneQueue.session_name == session_name)
        if confirmed_status is not None:
            sql = sql.where(PhoneQueue.confirmed_status == confirmed_status)
        if status is not None:
            sql = sql.where(PhoneQueue.status == status)
        if auth_proxy is not None:
            sql = sql.where(PhoneQueue.auth_proxy == auth_proxy)
        if statuses is not None:
            conditions = [PhoneQueue.status == status for status in statuses]
            sql = sql.where(or_(*conditions))
        if group_bot_message_id is not None:
            sql = sql.where(PhoneQueue.group_bot_message_id == group_bot_message_id)
        if group_user_message_id is not None:
            sql = sql.where(PhoneQueue.group_user_message_id == group_user_message_id)
        if drop_bot_message_id is not None:
            sql = sql.where(PhoneQueue.drop_bot_message_id == drop_bot_message_id)
        if drop_user_message_id is not None:
            sql = sql.where(PhoneQueue.drop_user_message_id == drop_user_message_id)
        if waiting_confirm_status is not None:
            sql = sql.where(PhoneQueue.waiting_confirm_status == waiting_confirm_status)
        if withdraw_status is not None:
            sql = sql.where(PhoneQueue.withdraw_status == withdraw_status)
        if pre_withdraw_statuses is not None:
            conditions = [PhoneQueue.pre_withdraw_status == pre_withdraw_status for pre_withdraw_status in pre_withdraw_statuses]
        if cryptobot_admin_notify is not None:
            sql = sql.where(PhoneQueue.cryptobot_admin_notify == cryptobot_admin_notify)
        if sent_sms_status is not None:
            sql = sql.where(PhoneQueue.sent_sms_status == sent_sms_status)
        if skip_count is not None:
            sql = sql.where(PhoneQueue.skip_count == skip_count)
        if skip_group_id_1 is not None:
            sql = sql.where(PhoneQueue.skip_group_id_1 == skip_group_id_1)
        if skip_group_id_2 is not None:
            sql = sql.where(PhoneQueue.skip_group_id_2 == skip_group_id_2)
        if not_skip_group_id_1 is not None:
            sql = sql.where(or_(PhoneQueue.skip_group_id_1 != not_skip_group_id_1, PhoneQueue.skip_group_id_1.is_(None)))
        if not_skip_group_id_2 is not None:
            sql = sql.where(or_(PhoneQueue.skip_group_id_2 != not_skip_group_id_2, PhoneQueue.skip_group_id_2.is_(None)))
        if sort_asc:
            sql = sql.order_by(PhoneQueue.added_at.asc())
        if sort_desc:
            sql = sql.order_by(PhoneQueue.added_at.desc())
        await session.execute(sql.values(data))
        await session.commit()

