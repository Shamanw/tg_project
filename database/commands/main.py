import time
import json
import traceback

from decimal import Decimal
from typing import *
from datetime import datetime, timedelta
from datetime import time as dt_time
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.engine import get_session
from database.tables import *


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, User):
            return obj.to_dict()
        return super().default(obj)


def sqlalchemy_to_dict(obj, max_depth=1, current_depth=0):
    if isinstance(obj, list):
        return [sqlalchemy_to_dict(item, max_depth, current_depth) for item in obj]
    if isinstance(obj, dict):
        return {
            key: sqlalchemy_to_dict(value, max_depth, current_depth)
            for key, value in obj.items()
        }
    if not hasattr(obj, '__table__') and not hasattr(obj, '__mapper__'):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    result = {}
    mapper = inspect(obj).mapper
    for column in mapper.column_attrs:
        val = getattr(obj, column.key)
        if isinstance(val, Decimal):
            val = float(val)
        elif isinstance(val, datetime):
            val = val.isoformat()
        result[column.key] = val
    if current_depth < max_depth:
        for rel in mapper.relationships:
            related_val = getattr(obj, rel.key)
            result[rel.key] = sqlalchemy_to_dict(
                related_val,
                max_depth=max_depth,
                current_depth=current_depth+1
            )
    return result


def parse_r_date(date_str: str):
    day, month, year = map(int, date_str.split('.'))
    return datetime(year, month, day)


class TimeFilter:
    def __init__(self, field_name: str, value: str, 
                 single_date: str = None, 
                 start_date_str: str = None, 
                 end_date_str: str = None, 
                 custom_days: int = None):
        self.field_name = field_name
        self.value = value.lower() if value else ''
        self.now = datetime.now()

        self.single_date = single_date
        self.start_date_str = start_date_str
        self.end_date_str = end_date_str
        self.custom_days = custom_days

    def get_date_range(self):
        if self.value == 'today':
            start_date = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = self.now

        elif self.value.startswith('days'):
            days = int(self.value[4:])
            start_date = (self.now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = self.now

        elif self.value == 'custom':
            if not self.custom_days:
                return None, None
            days = int(self.custom_days)
            start_date = (self.now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = self.now

        elif self.value == 'yesterday':
            start_date = (self.now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif self.value == 'beforeyesterday':
            start_date = (self.now - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif self.value == 'week':
            start_date = (self.now - timedelta(days=self.now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = self.now

        elif self.value == 'month':
            start_date = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = self.now

        elif self.value == 'previousmonth':
            first_day_of_this_month = self.now.replace(day=1)
            last_day_of_prev_month = first_day_of_this_month - timedelta(days=1) 
            start_date = last_day_of_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = last_day_of_prev_month.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif self.value == 'singledate':
            if not self.single_date:
                return None, None
            dt_parsed = parse_r_date(self.single_date)
            start_date = dt_parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = dt_parsed.replace(hour=23, minute=59, second=59, microsecond=999999)

        elif self.value == 'daterange':
            if not self.start_date_str or not self.end_date_str:
                return None, None
            start_dt = parse_r_date(self.start_date_str)
            end_dt = parse_r_date(self.end_date_str)
            start_date = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        else:
            return None, None

        return start_date, end_date


async def add_record(table: Table, **data):
    async with get_session() as session:
        sql = table(**data)
        session.add(sql)
        try:
            await session.commit()
            await session.refresh(sql)
            record_id = sql.id
            return record_id
        except IntegrityError:
            await session.rollback()
            raise
    return None


async def select_one_record(table: Table, **filters):
    async with get_session() as session:
        query = select(table).limit(1)
        for field, value in filters.items():
            if isinstance(value, list):
                if field.endswith('_or'):
                    real_field = field.removesuffix('_or')
                    table_field = getattr(table, real_field)
                    query = query.where(or_(*[table_field == val for val in value]))
                elif field.endswith('_not_in'):
                    real_field = field.removesuffix('_not_in')
                    table_field = getattr(table, real_field)
                    query = query.where(~table_field.in_(value))
                elif field.endswith('_in'):
                    real_field = field.removesuffix('_in')
                    table_field = getattr(table, real_field)
                    query = query.where(table_field.in_(value))
                else:
                    query = query.where(getattr(table, field) == value)
            elif field.startswith('sort_'):
                direction = field.split('_')[1]
                if hasattr(table, value):
                    table_field = getattr(table, value)
                    if direction == 'desc':
                        query = query.order_by(desc(table_field))
                    elif direction == 'asc':
                        query = query.order_by(asc(table_field))
            elif field.endswith('_at') and isinstance(value, str):
                time_filter = TimeFilter(field, value)
                start_date, end_date = time_filter.get_date_range()
                if start_date is not None and end_date is not None:
                    query = query.where(
                        and_(
                            getattr(table, field) >= start_date,
                            getattr(table, field) <= end_date
                        )
                    )
            elif field.endswith('_equals_or_more'):
                real_field = field.removesuffix('_equals_or_more')
                query = query.where(getattr(table, real_field) >= value)
            elif field.endswith('_count_less'):
                real_field = field.removesuffix('_count_less')
                query = query.where(getattr(table, real_field) > value)
            elif field.endswith('_count_more'):
                real_field = field.removesuffix('_count_more')
                query = query.where(getattr(table, real_field) < value)
            elif field.endswith('_less'):
                real_field = field.removesuffix('_less')
                date_threshold = datetime.now() - timedelta(days=value)
                query = query.where(getattr(table, real_field) >= date_threshold)
            elif field.endswith('_more'):
                real_field = field.removesuffix('_more')
                date_threshold = datetime.now() - timedelta(days=value)
                query = query.where(getattr(table, real_field) <= date_threshold)
            elif field.endswith('_is_none'):
                real_field = field.removesuffix('_is_none')
                if value:
                    query = query.where(getattr(table, real_field).is_(None))
            elif field.endswith('_is_not_none'):
                real_field = field.removesuffix('_is_not_none')
                if value:
                    query = query.where(getattr(table, real_field).isnot(None))
            else:
                query = query.where(getattr(table, field) == value)
        result = await session.execute(query)
        return result.scalar()


async def select_many_records(table: Table, count = None, limit = None, offset = None, **filters):
    async with get_session() as session:
        if count:
            query = select(func.count()).select_from(table)
        else:
            query = select(table)
        for field, value in filters.items():
            if isinstance(value, list):
                if field.endswith('_or'):
                    real_field = field.removesuffix('_or')
                    table_field = getattr(table, real_field)
                    query = query.where(or_(*[table_field == val for val in value]))
                elif field.endswith('_not_in'):
                    real_field = field.removesuffix('_not_in')
                    table_field = getattr(table, real_field)
                    query = query.where(~table_field.in_(value))
                elif field.endswith('_in'):
                    real_field = field.removesuffix('_in')
                    table_field = getattr(table, real_field)
                    query = query.where(table_field.in_(value))
                else:
                    query = query.where(getattr(table, field) == value)
            elif field.startswith('sort_'):
                direction = field.split('_')[1]
                if hasattr(table, value):
                    table_field = getattr(table, value)
                    if direction == 'desc':
                        query = query.order_by(desc(table_field))
                    elif direction == 'asc':
                        query = query.order_by(asc(table_field))
            elif field.endswith('_at') and isinstance(value, str):
                time_filter = TimeFilter(field, value)
                start_date, end_date = time_filter.get_date_range()
                if start_date is not None and end_date is not None:
                    query = query.where(
                        and_(
                            getattr(table, field) >= start_date,
                            getattr(table, field) <= end_date
                        )
                    )
            elif field.endswith('_equals_or_more'):
                real_field = field.removesuffix('_equals_or_more')
                query = query.where(getattr(table, real_field) >= value)
            elif field.endswith('_count_less'):
                real_field = field.removesuffix('_count_less')
                query = query.where(getattr(table, real_field) > value)
            elif field.endswith('_count_more'):
                real_field = field.removesuffix('_count_more')
                query = query.where(getattr(table, real_field) < value)
            elif field.endswith('_less'):
                real_field = field.removesuffix('_less')
                date_threshold = datetime.now() - timedelta(days=value)
                query = query.where(getattr(table, real_field) >= date_threshold)
            elif field.endswith('_more'):
                real_field = field.removesuffix('_more')
                date_threshold = datetime.now() - timedelta(days=value)
                query = query.where(getattr(table, real_field) <= date_threshold)
            elif field.endswith('_is_none'):
                real_field = field.removesuffix('_is_none')
                if value:
                    query = query.where(getattr(table, real_field).is_(None))
            elif field.endswith('_is_not_none'):
                real_field = field.removesuffix('_is_not_none')
                if value:
                    query = query.where(getattr(table, real_field).isnot(None))
            else:
                query = query.where(getattr(table, field) == value)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        if count:
            result = await session.execute(query)
            return result.scalar()
        else:
            result = await session.execute(query)
            return result.scalars().all()

async def update_record(table: Table, data: dict, update_limit_count: int = None, **filters):
    async with get_session() as session:
        filter_conditions = []
        
        for field, value in filters.items():
            if isinstance(value, list):
                if field.endswith('_or'):
                    real_field = field.removesuffix('_or')
                    table_field = getattr(table, real_field)
                    filter_conditions.append(or_(*[table_field == val for val in value]))
                elif field.endswith('_not_in'):
                    real_field = field.removesuffix('_not_in')
                    table_field = getattr(table, real_field)
                    query = query.where(~table_field.in_(value))
                elif field.endswith('_in'):
                    real_field = field.removesuffix('_in')
                    table_field = getattr(table, real_field)
                    filter_conditions.append(table_field.in_(value))
                else:
                    filter_conditions.append(getattr(table, field) == value)
            
            elif field.startswith('sort_'):
                direction = field.split('_')[1]
                if hasattr(table, value):
                    table_field = getattr(table, value)
                    if direction == 'desc':
                        query = query.order_by(desc(table_field))
                    elif direction == 'asc':
                        query = query.order_by(asc(table_field))
            
            elif field.endswith('_at') and isinstance(value, str):
                time_filter = TimeFilter(field, value)
                start_date, end_date = time_filter.get_date_range()
                if start_date is not None and end_date is not None:
                    filter_conditions.append(
                        and_(
                            getattr(table, field) >= start_date,
                            getattr(table, field) <= end_date
                        )
                    )
            
            elif field.endswith('_less'):
                real_field = field.removesuffix('_less')
                date_threshold = datetime.now() - timedelta(days=value)
                filter_conditions.append(getattr(table, real_field) >= date_threshold)
            
            elif field.endswith('_more'):
                real_field = field.removesuffix('_more')
                date_threshold = datetime.now() - timedelta(days=value)
                filter_conditions.append(getattr(table, real_field) <= date_threshold)
            
            elif field.endswith('_is_none'):
                real_field = field.removesuffix('_is_none')
                if value:
                    filter_conditions.append(getattr(table, real_field).is_(None))
            
            elif field.endswith('_is_not_none'):
                real_field = field.removesuffix('_is_not_none')
                if value:
                    filter_conditions.append(getattr(table, real_field).isnot(None))
            
            else:
                filter_conditions.append(getattr(table, field) == value)

        if update_limit_count:
            subquery = (
                select(table.id)
                .where(*filter_conditions)
                .limit(update_limit_count)
                .scalar_subquery()
            )
            query = update(table).where(table.id.in_(subquery)).values(data)
        else:
            query = update(table).where(*filter_conditions).values(data)

        try:
            await session.execute(query)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise

async def delete_record(table: Table, **filters):
    async with get_session() as session:
        query = delete(table)
        for field, value in filters.items():
            query = query.where(getattr(table, field) == value)
        try:
            await session.execute(query)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise


async def select_custom_query(query: str):
    query_upper = query.upper()
    if not query_upper.startswith('SELECT') or any(keyword in query_upper for keyword in ['UPDATE', 'DELETE', 'INSERT', 'DROP', 'ALTER']):
        return False
    
    async with get_session() as session:
        try:
            stmt = text(query)
            result = await session.execute(stmt)
            return result.all()
        except SQLAlchemyError as e:
            traceback.print_exc()
            print(f"Ошибка при выполнении запроса: {e}")
            return False






async def select_convert_history_writes(
        user_id = None,
        convert_type = None,
        count = None,
        total_amount = None,
        added_at_00_00 = None,
        added_at_yesterday = None,
        added_at_week = None,
        added_at_month = None,
        added_at_sort_asc = None,
        added_at_sort_desc = None,
):
    async with get_session() as session:
        if count:
            sql = select(func.count()).select_from(ConvertHistory)
        elif total_amount:
            sql = select(func.sum(ConvertHistory.total_amount))
        else:
            sql = select(ConvertHistory)
        if user_id is not None:
            sql = sql.where(ConvertHistory.user_id == user_id)
        if convert_type is not None:
            sql = sql.where(ConvertHistory.convert_type == convert_type)
        if added_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(ConvertHistory.added_at >= today_start).where(ConvertHistory.added_at <= today_end)
        if added_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(ConvertHistory.added_at >= yesterday_start).where(ConvertHistory.added_at <= yesterday_end)
        if added_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(ConvertHistory.added_at >= week_start).where(ConvertHistory.added_at <= week_end)
        if added_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(ConvertHistory.added_at >= month_start).where(ConvertHistory.added_at <= month_end)
        if count:
            result = await session.execute(sql)
            return result.scalar()
        else:
            if total_amount:
                sql = sql.where(ConvertHistory.total_amount != None, ConvertHistory.total_amount > 0)
                sum_result = await session.execute(sql)
                total_amount = sum_result.scalar()
                if total_amount is None or total_amount <= 0:
                    return 0
                else:
                    return total_amount
            if added_at_sort_asc:
                sql = sql.order_by(ConvertHistory.added_at.asc())
            if added_at_sort_desc:
                sql = sql.order_by(ConvertHistory.added_at.desc())
            result = await session.execute(sql)
            results = result.scalars().all()
            return results


async def select_usdt_payments_2(
        user_id = None,
        status = None,
        count = None,
        total_amount_usdt = None,
        added_at_00_00 = None,
        added_at_yesterday = None,
        added_at_week = None,
        added_at_month = None,
        added_at_sort_asc = None,
        added_at_sort_desc = None,
):
    async with get_session() as session:
        if count:
            sql = select(func.count()).select_from(Payment)
        elif total_amount_usdt:
            sql = select(func.sum(Payment.amount_usdt))
        else:
            sql = select(Payment)
        if user_id is not None:
            sql = sql.where(Payment.user_id == user_id)
        if status is not None:
            sql = sql.where(Payment.status == status)
        if added_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(Payment.added_at >= today_start).where(Payment.added_at <= today_end)
        if added_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(Payment.added_at >= yesterday_start).where(Payment.added_at <= yesterday_end)
        if added_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(Payment.added_at >= week_start).where(Payment.added_at <= week_end)
        if added_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(Payment.added_at >= month_start).where(Payment.added_at <= month_end)
        if count:
            result = await session.execute(sql)
            return result.scalar()
        else:
            if total_amount_usdt:
                sql = sql.where(Payment.amount_usdt != None, Payment.amount_usdt > 0)
                sum_result = await session.execute(sql)
                total_amount_usdt = sum_result.scalar()
                if total_amount_usdt is None or total_amount_usdt <= 0:
                    return 0
                else:
                    return total_amount_usdt
            if added_at_sort_asc:
                sql = sql.order_by(Payment.added_at.asc())
            if added_at_sort_desc:
                sql = sql.order_by(Payment.added_at.desc())
            result = await session.execute(sql)
            results = result.scalars().all()
            return results


async def select_cryptobot_payments_2(
        user_id = None,
        status = None,
        count = None,
        total_amount_usdt = None,
        added_at_00_00 = None,
        added_at_yesterday = None,
        added_at_week = None,
        added_at_month = None,
        added_at_sort_asc = None,
        added_at_sort_desc = None,
):
    async with get_session() as session:
        if count:
            sql = select(func.count()).select_from(CryptoBotPayment)
        elif total_amount_usdt:
            sql = select(func.sum(CryptoBotPayment.amount_usdt))
        else:
            sql = select(CryptoBotPayment)
        if user_id is not None:
            sql = sql.where(CryptoBotPayment.user_id == user_id)
        if status is not None:
            sql = sql.where(CryptoBotPayment.status == status)
        if added_at_00_00:
            today_start = datetime.combine(datetime.today(), dt_time.min)
            today_end = datetime.combine(datetime.today(), dt_time.max)
            sql = sql.where(CryptoBotPayment.added_at >= today_start).where(CryptoBotPayment.added_at <= today_end)
        if added_at_yesterday:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_start = datetime.combine(yesterday.date(), dt_time.min)
            yesterday_end = datetime.combine(yesterday.date(), dt_time.max)
            sql = sql.where(CryptoBotPayment.added_at >= yesterday_start).where(CryptoBotPayment.added_at <= yesterday_end)
        if added_at_week:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_start = datetime.combine(start_of_week.date(), dt_time.min)
            week_end = datetime.now()
            sql = sql.where(CryptoBotPayment.added_at >= week_start).where(CryptoBotPayment.added_at <= week_end)
        if added_at_month:
            today = datetime.today()
            start_of_month = today.replace(day=1)
            month_start = datetime.combine(start_of_month.date(), dt_time.min)
            month_end = datetime.now()
            sql = sql.where(CryptoBotPayment.added_at >= month_start).where(CryptoBotPayment.added_at <= month_end)
        if count:
            result = await session.execute(sql)
            return result.scalar()
        else:
            if total_amount_usdt:
                sql = sql.where(CryptoBotPayment.amount_usdt != None, CryptoBotPayment.amount_usdt > 0)
                sum_result = await session.execute(sql)
                total_amount_usdt = sum_result.scalar()
                if total_amount_usdt is None or total_amount_usdt <= 0:
                    return 0
                else:
                    return total_amount_usdt
            if added_at_sort_asc:
                sql = sql.order_by(CryptoBotPayment.added_at.asc())
            if added_at_sort_desc:
                sql = sql.order_by(CryptoBotPayment.added_at.desc())
            result = await session.execute(sql)
            results = result.scalars().all()
            return results
