from typing import *
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from config import *

from database.engine import get_session
from database.tables import ConverterProxySocks5


async def add_converter_proxy_socks_5(
        scheme = None,
        login = None,
        password = None,
        ip = None,
        port = None
    ):
    async with get_session() as session:
        sql = ConverterProxySocks5(
            scheme=scheme,
            login=login,
            password=password,
            ip=ip,
            port=port
        )
        session.add(sql)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        await session.refresh(sql)
        return sql


async def select_converter_proxy_socks_5(
        scheme = None,
        login = None,
        password = None,
        ip = None,
        port = None,
    ):
    async with get_session() as session:
        sql = select(ConverterProxySocks5).limit(1).order_by(func.random()) 
        if scheme is not None:
            sql = sql.where(ConverterProxySocks5.scheme == scheme)
        if login is not None:
            sql = sql.where(ConverterProxySocks5.login == login)
        if password is not None:
            sql = sql.where(ConverterProxySocks5.password == password)
        if ip is not None:
            sql = sql.where(ConverterProxySocks5.ip == ip)
        if port is not None:
            sql = sql.where(ConverterProxySocks5.port == port)
        result = await session.execute(sql)
        return result.scalar()


async def select_converter_proxy_socks_5s(
        scheme = None,
        login = None,
        password = None,
        not_password = None,
        ip = None,
        port = None,
):
    async with get_session() as session:
        sql = select(ConverterProxySocks5)
        if scheme is not None:
            sql = sql.where(ConverterProxySocks5.scheme == scheme)
        if login is not None:
            sql = sql.where(ConverterProxySocks5.login == login)
        if password is not None:
            sql = sql.where(ConverterProxySocks5.password == password)
        if not_password is not None:
            sql = sql.where(ConverterProxySocks5.password != not_password)
        if ip is not None:
            sql = sql.where(ConverterProxySocks5.ip == ip)
        if port is not None:
            sql = sql.where(ConverterProxySocks5.port == port)
        result = await session.execute(sql)
        results = result.scalars().all()
        return results


async def update_converter_proxy_socks_5(
        scheme = None,
        login = None,
        password = None,
        not_password = None,
        ip = None,
        port = None,
        data = None,
):
    async with get_session() as session:
        sql = update(ConverterProxySocks5)
        if scheme is not None:
            sql = sql.where(ConverterProxySocks5.scheme == scheme)
        if login is not None:
            sql = sql.where(ConverterProxySocks5.login == login)
        if password is not None:
            sql = sql.where(ConverterProxySocks5.password == password)
        if not_password is not None:
            sql = sql.where(ConverterProxySocks5.password != not_password)
        if ip is not None:
            sql = sql.where(ConverterProxySocks5.ip == ip)
        if port is not None:
            sql = sql.where(ConverterProxySocks5.port == port)
        await session.execute(sql.values(data))
        await session.commit()


async def delete_converter_proxy_socks_5(
        scheme = None,
        login = None,
        password = None,
        not_password = None,
        ip = None,
        port = None,
):
    async with get_session() as session:
        sql = delete(ConverterProxySocks5)
        if scheme is not None:
            sql = sql.where(ConverterProxySocks5.scheme == scheme)
        if login is not None:
            sql = sql.where(ConverterProxySocks5.login == login)
        if password is not None:
            sql = sql.where(ConverterProxySocks5.password == password)
        if not_password is not None:
            sql = sql.where(ConverterProxySocks5.password != not_password)
        if ip is not None:
            sql = sql.where(ConverterProxySocks5.ip == ip)
        if port is not None:
            sql = sql.where(ConverterProxySocks5.port == port)
        await session.execute(sql)
        await session.commit()

