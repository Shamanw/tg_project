import ast
import asyncio
import logging
import traceback

from asyncio import Semaphore
from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, FSInputFile
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.inline.misc_kb import *

from database.engine import create_base
from database.commands.main import *
from database.commands.users import *
from database.commands.phones_queue import *
from database.commands.groups import *
from database.commands.scheduler_text import *
from database.commands.scheduler_groups import *
from database.commands.scheduler_bot import *
from database.commands.saved_mass_ids import *
from database.commands.bot_settings import *
from database.commands.proxy_socks_5 import *
from database.commands.converter_proxy_socks_5 import *
from database.commands.withdraws import *

from middlewares.update_user_data import UpdateUserDataMiddleware
from middlewares.manual_check import ManualCheckMiddleware
from middlewares.sub_check import SubCheckMiddleware
from middlewares.clients_sub_check import ClientsSubCheckMiddleware

from handlers.admin import admin_router
from handlers.topic import topic_router
from handlers.client_group import client_group_router
from handlers.client_private import client_private_router
from handlers.drop import drop_router
from handlers.drop_or_client import drop_or_client_router
from handlers.clear_notify import clear_notify_router
from handlers.clients_private import clients_private_router
from handlers.clients_group import clients_group_router

# from utils.misc import different_time, get_phone_type_text, get_phone_queue, get_phone_type_command, find_inds, get_minutes_ban
from utils.misc import *
from utils.tele import *
from utils.additionally_bot import *

from config import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')



# alive_status = 0
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status
# alive_status

async def alive_check(bot):
    while True:
        bt = await select_bot_setting()
        try:
            writes = await select_many_records(PhoneQueue, status=18, slet_at_is_not_none=True, slet_at_more=7, alive_status=0)
            if writes:
                for write in writes:
                    logger.info(f'alive_check write: {write.phone_number} | {write.session_name}')
                    proxy_data = write.auth_proxy
                    if proxy_data:
                        proxy_data = {
                            "scheme": proxy_data['scheme'],
                            "hostname": proxy_data['hostname'],
                            "port": int(proxy_data['port']),
                            "username": proxy_data['username'],
                            "password": proxy_data['password']
                        }
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        proxy_data = await select_proxy_socks_5()
                        if proxy_data:
                            proxy_data = {
                                'scheme': proxy_data.scheme,
                                'hostname': proxy_data.ip,
                                'port': int(proxy_data.port),
                                'username': proxy_data.login,
                                'password': proxy_data.password
                            }
                        if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                            continue
                    try:
                        resp, resp2 = await asyncio.wait_for(
                            validate_session(write=write, proxy=proxy_data),
                            timeout=60
                        )
                    except (asyncio.TimeoutError, Exception):
                        resp, resp2 = None, None
                    if not resp and resp2 is not None:
                        logger.info(f'alive_check: Session invalidated: {write.phone_number} | {write.session_name}')
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.alive_status: 1,
                                PhoneQueue.alive_check_at: datetime.now()
                            }
                        )
                    else:
                        if resp and resp2:
                            try:
                                resp, resp2 = await asyncio.wait_for(
                                    account_is_frozen_status(write=write, proxy=proxy_data),
                                    timeout=60
                                )
                            except (asyncio.TimeoutError, Exception):
                                resp, resp2 = None, None
                            if resp and resp2:
                                logger.info(f'ACC_FROZEN: {write.phone_number} | {write.session_name}')
                                write = await select_phone_queue(primary_id=write.id)
                                await update_phone_queue(
                                    primary_id=write.id,
                                    data={
                                        PhoneQueue.status: 42,
                                        PhoneQueue.slet_at: datetime.now(),
                                        PhoneQueue.slet_main_at: datetime.now(),
                                    }
                                )
                                if write.status != 18:
                                    await BotSendMessage(
                                        bot,
                                        chat_id=bt.topic_id,
                                        message_thread_id=bt.topic_frozen_theme_id,
                                        text=await get_frozen_session_info(user_info=await select_user(user_id=write.drop_id), write=write),
                                        reply_markup=multi_2_kb(
                                            text='🚷 Заблокировать', callback_data=f'TOPIC_US|{write.id}|BAN', 
                                            text_back='☑️ Разблокировать', callback_data_back=f'TOPIC_US|{write.id}|UNBAN', 
                                        ),
                                        disable_web_page_preview=True
                                    )
                            else:
                                try:
                                    resp, resp2 = await asyncio.wait_for(check_shadow_ban(write=write, proxy=proxy_data), timeout=60)
                                except asyncio.TimeoutError:
                                    logger.error(f'\n\n[app.py:check_shadow_ban] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                    resp, resp2 = None, None
                                except:
                                    resp, resp2 = None, None
                                if not resp and resp2 is not None:
                                    logger.info(f'alive_check: Shadow ban: {write.phone_number} | {write.session_name}')
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.alive_status: 2,
                                            PhoneQueue.alive_check_at: datetime.now()
                                        }
                                    )
                                else:
                                    if resp and resp2:
                                        try:
                                            resp, resp2 = await asyncio.wait_for(send_message_for_check_spam(write=write, proxy=proxy_data), timeout=60)
                                        except asyncio.TimeoutError:
                                            logger.error(f'\n\n[app.py:send_message_for_check_spam] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                            resp, resp2 = None, None
                                        except:
                                            resp, resp2 = None, None
                                        if not resp and resp2 is not None:
                                            logger.info(f'alive_check: Spamblock: {write.phone_number} | {write.session_name}')
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.alive_status: 3,
                                                    PhoneQueue.alive_check_at: datetime.now()
                                                }
                                            )
                                        else:
                                            if resp and resp2:
                                                logger.info(f'alive_check: ALIVE: {write.phone_number} | {write.session_name}')
                                                await update_phone_queue(
                                                    primary_id=write.id,
                                                    data={
                                                        PhoneQueue.status: 12,
                                                        PhoneQueue.alive_status: 9,
                                                        PhoneQueue.alive_hold_status: 1,
                                                        PhoneQueue.alive_check_at: datetime.now()
                                                    }
                                                )
                                                try:
                                                    resp, resp2 = await asyncio.wait_for(terminate_all_sessions(write=write, proxy=proxy_data), timeout=60)
                                                except asyncio.TimeoutError:
                                                    resp, resp2 = None, None
                                                except:
                                                    resp, resp2 = None, None

            writes = await select_many_records(PhoneQueue, status_in=[18,40], slet_at_is_not_none=True, alive_status=10)
            if writes:
                for write in writes:
                    logger.info(f'alive_check10 write: {write.phone_number} | {write.session_name}')
                    proxy_data = write.auth_proxy
                    if proxy_data:
                        proxy_data = {
                            "scheme": proxy_data['scheme'],
                            "hostname": proxy_data['hostname'],
                            "port": int(proxy_data['port']),
                            "username": proxy_data['username'],
                            "password": proxy_data['password']
                        }
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        proxy_data = await select_proxy_socks_5()
                        if proxy_data:
                            proxy_data = {
                                'scheme': proxy_data.scheme,
                                'hostname': proxy_data.ip,
                                'port': int(proxy_data.port),
                                'username': proxy_data.login,
                                'password': proxy_data.password
                            }
                        if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                            continue
                    try:
                        resp, resp2 = await asyncio.wait_for(
                            validate_session(write=write, proxy=proxy_data),
                            timeout=60
                        )
                    except (asyncio.TimeoutError, Exception):
                        resp, resp2 = None, None
                    if not resp and resp2 is not None:
                        logger.info(f'alive_check: Session invalidated: {write.phone_number} | {write.session_name}')
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.status: 18,
                                PhoneQueue.alive_status: 0,
                                PhoneQueue.alive_check_at: datetime.now()
                            }
                        )
                    else:
                        if resp and resp2:
                            try:
                                resp, resp2 = await asyncio.wait_for(
                                    account_is_frozen_status(write=write, proxy=proxy_data),
                                    timeout=60
                                )
                            except (asyncio.TimeoutError, Exception):
                                resp, resp2 = None, None
                            if resp and resp2:
                                logger.info(f'ACC_FROZEN: {write.phone_number} | {write.session_name}')
                                write = await select_phone_queue(primary_id=write.id)
                                await update_phone_queue(
                                    primary_id=write.id,
                                    data={
                                        PhoneQueue.status: 42,
                                        PhoneQueue.slet_at: datetime.now(),
                                        PhoneQueue.slet_main_at: datetime.now(),
                                    }
                                )
                                if write.status != 18:
                                    await BotSendMessage(
                                        bot,
                                        chat_id=bt.topic_id,
                                        message_thread_id=bt.topic_frozen_theme_id,
                                        text=await get_frozen_session_info(user_info=await select_user(user_id=write.drop_id), write=write),
                                        reply_markup=multi_2_kb(
                                            text='🚷 Заблокировать', callback_data=f'TOPIC_US|{write.id}|BAN', 
                                            text_back='☑️ Разблокировать', callback_data_back=f'TOPIC_US|{write.id}|UNBAN', 
                                        ),
                                        disable_web_page_preview=True
                                    )
                            else:
                                try:
                                    resp, resp2 = await asyncio.wait_for(check_shadow_ban(write=write, proxy=proxy_data), timeout=60)
                                except asyncio.TimeoutError:
                                    logger.error(f'\n\n[app.py:check_shadow_ban] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                    resp, resp2 = None, None
                                except:
                                    resp, resp2 = None, None
                                if not resp and resp2 is not None:
                                    logger.info(f'alive_check10: Shadow ban: {write.phone_number} | {write.session_name}')
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.status: 18,
                                            PhoneQueue.alive_status: 0,
                                            PhoneQueue.alive_check_at: datetime.now()
                                        }
                                    )
                                else:
                                    try:
                                        resp, resp2 = await asyncio.wait_for(send_message_for_check_spam(write=write, proxy=proxy_data), timeout=60)
                                    except asyncio.TimeoutError:
                                        logger.error(f'\n\n[app.py:send_message_for_check_spam] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                        resp, resp2 = None, None
                                    except:
                                        resp, resp2 = None, None
                                    if not resp and resp2 is not None:
                                        logger.info(f'alive_check10: Spamblock: {write.phone_number} | {write.session_name}')
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.status: 18,
                                                PhoneQueue.alive_status: 0,
                                                PhoneQueue.alive_check_at: datetime.now()
                                            }
                                        )
                                    else:
                                        if resp and resp2:
                                            logger.info(f'alive_check: ALIVE: {write.phone_number} | {write.session_name}')
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.status: 12,
                                                    PhoneQueue.alive_status: 9,
                                                    PhoneQueue.alive_check_at: datetime.now()
                                                }
                                            )
                                            try:
                                                resp, resp2 = await asyncio.wait_for(terminate_all_sessions(write=write, proxy=proxy_data), timeout=60)
                                            except asyncio.TimeoutError:
                                                resp, resp2 = None, None
                                            except:
                                                resp, resp2 = None, None

            writes = await select_many_records(PhoneQueue, status=18, slet_at_is_not_none=True, alive_last_check_status=1, alive_status=9)
            if writes:
                for write in writes:
                    logger.info(f'alive_check write: {write.phone_number} | {write.session_name}')
                    proxy_data = write.auth_proxy
                    if proxy_data:
                        proxy_data = {
                            "scheme": proxy_data['scheme'],
                            "hostname": proxy_data['hostname'],
                            "port": int(proxy_data['port']),
                            "username": proxy_data['username'],
                            "password": proxy_data['password']
                        }
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        proxy_data = await select_proxy_socks_5()
                        if proxy_data:
                            proxy_data = {
                                'scheme': proxy_data.scheme,
                                'hostname': proxy_data.ip,
                                'port': int(proxy_data.port),
                                'username': proxy_data.login,
                                'password': proxy_data.password
                            }
                        if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                            continue
                    try:
                        resp, resp2 = await asyncio.wait_for(
                            validate_session(write=write, proxy=proxy_data),
                            timeout=60
                        )
                    except (asyncio.TimeoutError, Exception):
                        resp, resp2 = None, None
                    if not resp and resp2 is not None:
                        logger.info(f'alive_check: Session invalidated: {write.phone_number} | {write.session_name}')
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.alive_status: 1,
                                PhoneQueue.alive_check_at: datetime.now()
                            }
                        )
                    else:
                        if resp and resp2:
                            try:
                                resp, resp2 = await asyncio.wait_for(
                                    account_is_frozen_status(write=write, proxy=proxy_data),
                                    timeout=60
                                )
                            except (asyncio.TimeoutError, Exception):
                                resp, resp2 = None, None
                            if resp and resp2:
                                logger.info(f'ACC_FROZEN: {write.phone_number} | {write.session_name}')
                                write = await select_phone_queue(primary_id=write.id)
                                await update_phone_queue(
                                    primary_id=write.id,
                                    data={
                                        PhoneQueue.status: 42,
                                        PhoneQueue.slet_at: datetime.now(),
                                        PhoneQueue.slet_main_at: datetime.now(),
                                    }
                                )
                                if write.status != 18:
                                    await BotSendMessage(
                                        bot,
                                        chat_id=bt.topic_id,
                                        message_thread_id=bt.topic_frozen_theme_id,
                                        text=await get_frozen_session_info(user_info=await select_user(user_id=write.drop_id), write=write),
                                        reply_markup=multi_2_kb(
                                            text='🚷 Заблокировать', callback_data=f'TOPIC_US|{write.id}|BAN', 
                                            text_back='☑️ Разблокировать', callback_data_back=f'TOPIC_US|{write.id}|UNBAN', 
                                        ),
                                        disable_web_page_preview=True
                                    )
                            else:
                                try:
                                    resp, resp2 = await asyncio.wait_for(check_shadow_ban(write=write, proxy=proxy_data), timeout=60)
                                except asyncio.TimeoutError:
                                    logger.error(f'\n\n[app.py:check_shadow_ban] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                    resp, resp2 = None, None
                                except:
                                    resp, resp2 = None, None
                                if not resp and resp2 is not None:
                                    logger.info(f'alive_check: Shadow ban: {write.phone_number} | {write.session_name}')
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.alive_status: 2,
                                            PhoneQueue.alive_check_at: datetime.now()
                                        }
                                    )
                                else:
                                    if resp and resp2:
                                        try:
                                            resp, resp2 = await asyncio.wait_for(send_message_for_check_spam(write=write, proxy=proxy_data), timeout=60)
                                        except asyncio.TimeoutError:
                                            logger.error(f'\n\n[app.py:send_message_for_check_spam] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                            resp, resp2 = None, None
                                        except:
                                            resp, resp2 = None, None
                                        if not resp and resp2 is not None:
                                            logger.info(f'alive_check: Spamblock: {write.phone_number} | {write.session_name}')
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.alive_status: 3,
                                                    PhoneQueue.alive_check_at: datetime.now()
                                                }
                                            )
                                        else:
                                            if resp and resp2:
                                                logger.info(f'alive_check: ALIVE: {write.phone_number} | {write.session_name}')
                                                await update_phone_queue(
                                                    primary_id=write.id,
                                                    data={
                                                        PhoneQueue.alive_status: 9,
                                                        PhoneQueue.alive_last_check_status: 2,
                                                        PhoneQueue.alive_check_at: datetime.now()
                                                    }
                                                )
                                                try:
                                                    resp, resp2 = await asyncio.wait_for(terminate_all_sessions(write=write, proxy=proxy_data), timeout=60)
                                                except asyncio.TimeoutError:
                                                    resp, resp2 = None, None
                                                except:
                                                    resp, resp2 = None, None
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(60)












async def pslet_check(bot):
    while True:
        bt = await select_bot_setting()
        date = datetime.now()
        try:
            if bt.pslet_status == 1 and bt.percent_slet:
                threshold = bt.percent_slet
                drops = await select_many_records(User, is_banned=0, role='drop')
                if drops:
                    for drop in drops:
                        if drop.auto_withdraw_status == 0:
                            slet_count = await select_many_records(PhoneQueue, awd_check_status=0, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status=18, slet_main_at_is_not_none=True)
                            slet_count += await select_many_records(PhoneQueue, awd_check_status=0, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_in=[1,2,3], slet_main_at_is_not_none=True)
                            slet_count += await select_many_records(PhoneQueue, awd_check_status=0, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_not_in=[1,2,3], alive_hold_status=1, buyed_at_is_not_none=True)
                            print(f'[pslet_check - {date} - A_W_S/SLET] [{drop.user_id}] slet_count: {slet_count}')
                            # buyed_count = await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, status=17, buyed_at_is_not_none=True)
                            buyed_count = await select_many_records(PhoneQueue, awd_check_status=0, pslet_status=0, count=True, drop_id=drop.user_id, set_at_is_not_none=True)
                            total_count = slet_count + buyed_count
                            print(f'[pslet_check - {date} - A_W_S/SLET] [{drop.user_id}] total_count: {total_count}')
                            if total_count and buyed_count >= 30:
                                if not drop.hold_check_expired_at:
                                    await update_user(user_id=drop.user_id, data={User.hold_check_expired_at: datetime.now() + timedelta(hours=12)})
                                    continue
                                elif drop.hold_check_expired_at and datetime.now() >= drop.hold_check_expired_at:
                                    slet_percentage = round((slet_count / total_count) * 100, 2)
                                    print(f'[pslet_check - {date} - A_W_S/SLET] [{drop.user_id}] slet_percentage: {slet_percentage}/{threshold}% | slet_count/buyed_count/total_count: {slet_count}/{buyed_count}/{total_count}')
                                    if slet_percentage >= threshold:
                                        await update_user(user_id=drop.user_id, data={User.is_banned: 1, User.auto_ban_status: 1, User.auto_ban_count: User.auto_ban_count + 1})
                                        await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status=18, slet_main_at_is_not_none=True, data={PhoneQueue.pslet_status: 1, PhoneQueue.awd_check_status: 1})
                                        await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_in=[1,2,3], slet_main_at_is_not_none=True, data={PhoneQueue.pslet_status: 1, PhoneQueue.awd_check_status: 1})
                                        await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_not_in=[1,2,3], alive_hold_status=1, buyed_at_is_not_none=True, data={PhoneQueue.pslet_status: 1, PhoneQueue.awd_check_status: 1})
                                        await update_record(PhoneQueue, drop_id=drop.user_id, set_at_is_not_none=True, data={PhoneQueue.awd_check_status: 1})
                                        # await update_record(PhoneQueue, drop_id=drop.user_id, confirmed_status=1, withdraw_status=0, pre_withdraw_status_in=[0,1], data={PhoneQueue.pre_withdraw_status: 3}) # аннулирование баланса
                                        await BotSendMessage(
                                            bot, 
                                            chat_id=drop.user_id, 
                                            text=(
                                                f'<b>⛔️ Вы заблокированы в боте за превышение допустимого порога слётов</b>'
                                                f'\n<b>Количество слетевших аккаунтов больше чем выданных или оплаченных:</b> <code>{slet_percentage}/{threshold}%</code>'
                                            )
                                        )
                                        await BotSendMessage(
                                            bot,
                                            chat_id=bt.topic_id,
                                            message_thread_id=bt.topic_bans_theme_id,
                                            text=(
                                                f'<b>⛔️💢 Автоблокировка новорега (слёты)</b>'
                                                f'\n<b>├ Процент:</b> <code>{slet_percentage}/{threshold}%</code>'
                                                f'\n<b>├ Оплаченных:</b> <code>{buyed_count}</code>'
                                                f'\n<b>├ Слетевших:</b> <code>{slet_count}</code>'
                                                f'{await get_user_bans_theme_info(user_info=drop)}'
                                            ),
                                            disable_web_page_preview=True
                                        )
                                    else:
                                        await update_user(user_id=drop.user_id, data={User.auto_withdraw_status: 1})
                        else:
                            if not drop.phones_added_ban_expired_at or (drop.phones_added_ban_expired_at and datetime.now() >= drop.phones_added_ban_expired_at):
                                slet_count = await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status=18, slet_main_at='month', slet_main_at_is_not_none=True)
                                slet_count += await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_in=[1,2,3], slet_main_at='month', slet_main_at_is_not_none=True)
                                slet_count += await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_not_in=[1,2,3], alive_hold_status=1, buyed_at='month', buyed_at_is_not_none=True)
                                print(f'[pslet_check - {date} - SLET] [{drop.user_id}] slet_count: {slet_count}')
                                if slet_count:
                                    buyed_count = await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, status=17, buyed_at='month', buyed_at_is_not_none=True)
                                    total_count = slet_count + buyed_count
                                    print(f'[pslet_check - {date} - SLET] [{drop.user_id}] total_count: {total_count}')
                                    if total_count and total_count >= 1:
                                        slet_percentage = round((slet_count / total_count) * 100, 2)
                                        print(f'[pslet_check - {date} - SLET] [{drop.user_id}] slet_percentage: {slet_percentage}/{threshold}% | slet_count/buyed_count/total_count: {slet_count}/{buyed_count}/{total_count}')
                                        if slet_percentage >= threshold:
                                            await update_user(user_id=drop.user_id, data={User.is_banned: 1, User.auto_ban_status: 1, User.auto_ban_count: User.auto_ban_count + 1})
                                            await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status=18, slet_main_at='month', slet_main_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
                                            await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_in=[1,2,3], slet_main_at='month', slet_main_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
                                            await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status=17, alive_status_not_in=[1,2,3], alive_hold_status=1, buyed_at='month', buyed_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
                                            # await update_record(PhoneQueue, drop_id=drop.user_id, confirmed_status=1, withdraw_status=0, pre_withdraw_status_in=[0,1], data={PhoneQueue.pre_withdraw_status: 3}) # аннулирование баланса
                                            await BotSendMessage(
                                                bot, 
                                                chat_id=drop.user_id, 
                                                text=(
                                                    f'<b>⛔️ Вы заблокированы в боте за превышение допустимого порога слётов</b>'
                                                    f'\n<b>Количество слетевших аккаунтов больше чем выданных:</b> <code>{slet_percentage}/{threshold}%</code>'
                                                )
                                            )
                                            await BotSendMessage(
                                                bot,
                                                chat_id=bt.topic_id,
                                                message_thread_id=bt.topic_bans_theme_id,
                                                text=(
                                                    f'<b>⛔️💢 Автоблокировка (слёты)</b>'
                                                    f'\n<b>├ Процент:</b> <code>{slet_percentage}/{threshold}%</code>'
                                                    f'\n<b>├ Выданных:</b> <code>{buyed_count}</code>'
                                                    f'\n<b>├ Слетевших:</b> <code>{slet_count}</code>'
                                                    f'{await get_user_bans_theme_info(user_info=drop)}'
                                                ),
                                                disable_web_page_preview=True
                                            )

            if bt.pslet_nevalid_status == 1 and bt.percent_nevalid:
                threshold = bt.percent_nevalid
                drops = await select_many_records(User, is_banned=0, role='drop')
                if drops:
                    for drop in drops:
                        if drop.auto_withdraw_status == 0:
                            nevalid_count = await select_many_records(PhoneQueue, awd_check_status=0, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status_in=[23,24], slet_main_at_is_not_none=True)
                            print(f'[pslet_check - {date} - A_W_S/NEVALID] [{drop.user_id}] nevalid_count: {nevalid_count}')
                            buyed_count = await select_many_records(PhoneQueue, awd_check_status=0, pslet_status=0, count=True, drop_id=drop.user_id, set_at_is_not_none=True)
                            total_count = nevalid_count + buyed_count
                            print(f'[pslet_check - {date} - A_W_S/NEVALID] [{drop.user_id}] total_count: {total_count}')
                            if total_count and buyed_count >= 30:
                                if not drop.hold_check_expired_at:
                                    await update_user(user_id=drop.user_id, data={User.hold_check_expired_at: datetime.now() + timedelta(hours=12)})
                                    continue
                                elif drop.hold_check_expired_at and datetime.now() >= drop.hold_check_expired_at:
                                    nevalid_percentage = round((nevalid_count / total_count) * 100, 2)
                                    print(f'[pslet_check - {date} - A_W_S/NEVALID] [{drop.user_id}] nevalid_percentage: {nevalid_percentage}/{threshold}% | nevalid_count/buyed_count/total_count: {nevalid_count}/{buyed_count}/{total_count}')
                                    if nevalid_percentage >= threshold:
                                        await update_user(user_id=drop.user_id, data={User.is_banned: 1, User.auto_ban_status: 1, User.auto_ban_count: User.auto_ban_count + 1})
                                        await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status_in=[23,24], slet_main_at_is_not_none=True, data={PhoneQueue.pslet_status: 1, PhoneQueue.awd_check_status: 1})
                                        await update_record(PhoneQueue, drop_id=drop.user_id, set_at_is_not_none=True, data={PhoneQueue.awd_check_status: 1})
                                        
                                        # await update_record(PhoneQueue, drop_id=drop.user_id, confirmed_status=1, withdraw_status=0, pre_withdraw_status_in=[0,1], data={PhoneQueue.pre_withdraw_status: 3}) # аннулирование баланса
                                        await BotSendMessage(
                                            bot, 
                                            chat_id=drop.user_id, 
                                            text=(
                                                f'<b>⛔️ Вы заблокированы в боте за превышение допустимого порога слётов</b>'
                                                f'\n<b>Количество невалидных аккаунтов больше чем оплаченных:</b> <code>{nevalid_percentage}/{threshold}%</code>'
                                            )
                                        )
                                        await BotSendMessage(
                                            bot,
                                            chat_id=bt.topic_id,
                                            message_thread_id=bt.topic_bans_theme_id,
                                            text=(
                                                f'<b>⛔️☠️ Автоблокировка новорега (невалид)</b>'
                                                f'\n<b>├ Процент:</b> <code>{nevalid_percentage}/{threshold}%</code>'
                                                f'\n<b>├ Оплаченных:</b> <code>{buyed_count}</code>'
                                                f'\n<b>├ Невалидных:</b> <code>{nevalid_count}</code>'
                                                f'{await get_user_bans_theme_info(user_info=drop)}'
                                            ),
                                            disable_web_page_preview=True
                                        )
                                    else:
                                        await update_user(user_id=drop.user_id, data={User.auto_withdraw_status: 1})
                        else:
                            if not drop.phones_added_ban_expired_at or (drop.phones_added_ban_expired_at and datetime.now() >= drop.phones_added_ban_expired_at):
                                nevalid_count = await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, unban_month_status=0, status_in=[23,24], slet_main_at='month', slet_main_at_is_not_none=True)
                                print(f'[pslet_check - {date} - NEVALID] [{drop.user_id}] nevalid_count: {nevalid_count}')
                                if nevalid_count:
                                    buyed_count = await select_many_records(PhoneQueue, pslet_status=0, count=True, drop_id=drop.user_id, set_at='month', set_at_is_not_none=True)
                                    total_count = nevalid_count + buyed_count
                                    print(f'[pslet_check - {date} - NEVALID] [{drop.user_id}] total_count: {total_count}')
                                    if total_count and total_count >= 10:
                                        nevalid_percentage = round((nevalid_count / total_count) * 100, 2)
                                        print(f'[pslet_check - {date} - NEVALID] [{drop.user_id}] nevalid_percentage: {nevalid_percentage}/{threshold}% | nevalid_count/buyed_count/total_count: {nevalid_count}/{buyed_count}/{total_count}')
                                        if nevalid_percentage >= threshold:
                                            await update_user(user_id=drop.user_id, data={User.is_banned: 1, User.auto_ban_status: 1, User.auto_ban_count: User.auto_ban_count + 1})
                                            await update_record(PhoneQueue, drop_id=drop.user_id, unban_month_status=0, status_in=[23,24], slet_main_at='month', slet_main_at_is_not_none=True, data={PhoneQueue.pslet_status: 1})
                                            # await update_record(PhoneQueue, drop_id=drop.user_id, confirmed_status=1, withdraw_status=0, pre_withdraw_status_in=[0,1], data={PhoneQueue.pre_withdraw_status: 3}) # аннулирование баланса
                                            await BotSendMessage(
                                                bot, 
                                                chat_id=drop.user_id, 
                                                text=(
                                                    f'<b>⛔️ Вы заблокированы в боте за превышение допустимого порога слётов</b>'
                                                    f'\n<b>Количество невалидных аккаунтов больше чем оплаченных:</b> <code>{nevalid_percentage}/{threshold}%</code>'
                                                )
                                            )
                                            await BotSendMessage(
                                                bot,
                                                chat_id=bt.topic_id,
                                                message_thread_id=bt.topic_bans_theme_id,
                                                text=(
                                                    f'<b>⛔️☠️ Автоблокировка (невалид)</b>'
                                                    f'\n<b>├ Процент:</b> <code>{nevalid_percentage}/{threshold}%</code>'
                                                    f'\n<b>├ Оплаченных:</b> <code>{buyed_count}</code>'
                                                    f'\n<b>├ Невалидных:</b> <code>{nevalid_count}</code>'
                                                    f'{await get_user_bans_theme_info(user_info=drop)}'
                                                ),
                                                disable_web_page_preview=True
                                            )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(600)















class PhoneQueueProcessor:
    def __init__(self):
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.completed_ids: Set[int] = set()
        self.lock = asyncio.Lock()

    async def process_single_phone(self, write, bot):
        try:
            bt = await select_bot_setting()
            write = await select_phone_queue(primary_id=write.id)
    
            if write.status == 0 and len(await select_phone_queues(drop_id=write.drop_id, status=1)) in [0, 1]:
                if write.last_check_at and await different_time(write.last_check_at, 16):
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.status: 2,
                        }
                    )
                    await BotSendMessage(
                        bot,
                        chat_id=write.drop_id,
                        text=f'<b>⚠️ Не удалось отправить СМС код на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                    )
                    return

                proxy_data = await select_proxy_socks_5()
                if not proxy_data:
                    if write.not_proxy_notify_status == 0:
                        await update_phone_queue(primary_id=write.id, data={PhoneQueue.not_proxy_notify_status: 1})
                        await BotSendMessage(
                            bot,
                            chat_id=bt.topic_id,
                            message_thread_id=bt.topic_not_found_proxy_theme_id,
                            text=f'<b>❗️ Нет прокси для авторизации номера <code>{write.phone_number}</code></b>'
                        )
                else:
                    proxy_data = {'scheme': proxy_data.scheme, 'hostname': proxy_data.ip, 'port': int(proxy_data.port), 'username': proxy_data.login, 'password': proxy_data.password}
                    if await check_proxy(proxy_data):
                        if not write.sent_code_at or (write.sent_code_at and await different_time(write.sent_code_at, 3)):
                            try:
                                resp, resp2 = await asyncio.wait_for(send_auth_code(phone=write.phone_number, proxy=proxy_data), timeout=60)
                            except asyncio.TimeoutError:
                                resp, resp2 = None, None
                            except:
                                resp, resp2 = None, None
                            if not resp and resp2 is not None:
                                if resp2 == 'send_error':
                                    status = 27
                                    text = f'<b>⚠️ Не удалось отправить СМС код на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2.startswith('flood_wait'):
                                    status = 10
                                    text = f'<b>⚠️ На номере <code>{write.phone_number}</code> ограничение на отправку кода, добавьте номер ещё раз через {resp2.split("|")[1]} сек.</b>'
                                elif resp2 == 'invalid_phone':
                                    status = 28
                                    text = f'<b>📵 Вы ввели неверный номер телефона <code>{write.phone_number}</code>, авторизация отменена.</b>'
                                elif resp2 == 'phone_banned':
                                    status = 26
                                    text = f'<b>⛔️ Номер телефона <code>{write.phone_number}</code> заблокирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'phone_unregistered':
                                    status = 29
                                    text = f'<b>❓ Номер телефона <code>{write.phone_number}</code> не зарегистрирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'frozen_method_invalid':
                                    status = 41
                                    text = f'<b>⛔️ Аккаунт <code>{write.phone_number}</code> заморожен, авторизация отменена.</b>'
                                else:
                                    status = None
                                    text = None
                                if status and text:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.auth_proxy: proxy_data,
                                            PhoneQueue.last_check_at: datetime.now(),
                                            PhoneQueue.sent_sms_status: 1,
                                            PhoneQueue.status: status,
                                        }
                                    )
                                    await BotSendMessage(
                                        bot,
                                        chat_id=write.drop_id,
                                        text=text
                                    )
                            else:
                                if resp and resp2:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.session_name: resp,
                                            PhoneQueue.phone_code_hash: resp2,
                                            PhoneQueue.auth_proxy: proxy_data,
                                            PhoneQueue.sent_sms_status: 1,
                                            PhoneQueue.status: 1,
                                            PhoneQueue.last_check_at: datetime.now(),
                                            PhoneQueue.sent_code_at: datetime.now(),
                                        }
                                    )
                                    response = await BotSendMessage(
                                        bot,
                                        chat_id=write.drop_id,
                                        text=(
                                            f'<b>🔔 Введите ответом на данное сообщение код из сообщения телеграм для авторизации аккаунта <code>{write.phone_number}</code></b>'
                                            '\n\n<b>❗️ Перед вводом кода поставьте точку, чтобы он автоматически не сбросился из-за подозрений в фишинге! (пример сообщения: <code>.12345</code>)</b>'
                                            '\n\n<b>‼️ У вас есть 5 минут</b>'
                                            f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
                                        ),
                                        reply_markup=multi_kb(
                                            text='❌ Отменить', callback_data=f'DROP_WORK|OTMENA|{write.id}'
                                        )
                                    )
                                    await delete_proxy_socks_5(scheme=proxy_data['scheme'], login=proxy_data['username'], password=proxy_data['password'], ip=proxy_data['hostname'], port=proxy_data['port'])
                                    try:
                                        if response:
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.drop_bot_message_id: response.message_id if response else None,
                                                }
                                            )
                                    except:
                                        pass
                                else:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.auth_proxy: proxy_data,
                                            PhoneQueue.sent_sms_status: 1,
                                        }
                                    )

            elif write.status == 1 and await different_time(write.last_check_at, 5):
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.status: 3,
                    }
                )
                await BotSendMessage(
                    bot,
                    chat_id=write.drop_id,
                    text=f'<b>❌ Вы не прислали код на номер <code>{write.phone_number}</code>, авторизация отменена.</b>'
                )
                try:
                    if write.drop_bot_message_id:
                        await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                except:
                    pass

            elif write.status == 6:
                proxy_data = write.auth_proxy
                if proxy_data:
                    proxy_data = {"scheme": proxy_data['scheme'], "hostname": proxy_data['hostname'], "port": int(proxy_data['port']), "username": proxy_data['username'], "password": proxy_data['password']}
                if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                    proxy_data = await select_proxy_socks_5()
                    if proxy_data:
                        proxy_data = {'scheme': proxy_data.scheme, 'hostname': proxy_data.ip, 'port': int(proxy_data.port), 'username': proxy_data.login, 'password': proxy_data.password}
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        logger.error(f'[{write.id} > {write.phone_number}] pass: {write.password} > НЕТ ПРОКСИ ДЛЯ УСТАНОВКИ ПАРОЛЯ')
                        if await different_time(write.last_check_at, 30):
                            if write.password and write is not None:
                                await update_phone_queue(
                                    primary_id=write.id,
                                    data={
                                        PhoneQueue.status: 8,
                                        PhoneQueue.last_check_at: datetime.now(),
                                    }
                                )
                                response = await BotSendMessage(
                                    bot,
                                    chat_id=write.drop_id,
                                    text=(
                                        f'<b>✅ Пароль успешно установлен на <code>{write.phone_number}</code></b>'
                                        '\n<b>ℹ️ Исключите в устройствах все сессии кроме недавно вошедшей и выйдите из аккаунта.</b>'
                                        '\n<b>❗️ У вас есть 20 минут до отмены</b>'
                                    )
                                )
                                try:
                                    try:
                                        if write.drop_bot_message_id:
                                            await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                    except:
                                        pass
                                    if response:
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.drop_bot_message_id: response.message_id if response else None,
                                            }
                                        )
                                except:
                                    pass
                            else:
                                await update_phone_queue(
                                    primary_id=write.id,
                                    data={
                                        PhoneQueue.status: 32,
                                    }
                                )
                                await BotSendMessage(
                                    bot,
                                    chat_id=write.drop_id,
                                    text=f'<b>❌ Не удалось установить пароль на аккаунте <code>{write.phone_number}</code>, авторизация отменена, повторите добавление ещё раз немного позже.</b>'
                                )
                                try:
                                    await delete_2fa(await select_phone_queue(primary_id=write.id), proxy_data)
                                except:
                                    pass
                                try:
                                    if write.drop_bot_message_id:
                                        await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                except:
                                    pass
                                return
                        else:
                            return

                if proxy_data:
                    if await different_time(write.last_check_at, 30):
                        if write.password and write is not None:
                            await update_phone_queue(
                                primary_id=write.id,
                                data={
                                    PhoneQueue.status: 8,
                                    PhoneQueue.last_check_at: datetime.now(),
                                }
                            )
                            response = await BotSendMessage(
                                bot,
                                chat_id=write.drop_id,
                                text=(
                                    f'<b>✅ Пароль успешно установлен на <code>{write.phone_number}</code></b>'
                                    '\n<b>ℹ️ Исключите в устройствах все сессии кроме недавно вошедшей и выйдите из аккаунта.</b>'
                                    '\n<b>❗️ У вас есть 20 минут до отмены</b>'
                                )
                            )
                            try:
                                try:
                                    if write.drop_bot_message_id:
                                        await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                except:
                                    pass
                                if response:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.drop_bot_message_id: response.message_id if response else None,
                                        }
                                    )
                            except:
                                pass
                        else:
                            await update_phone_queue(
                                primary_id=write.id,
                                data={
                                    PhoneQueue.status: 7,
                                }
                            )
                            await BotSendMessage(
                                bot,
                                chat_id=write.drop_id,
                                text=f'<b>❌ Не удалось установить пароль на аккаунте <code>{write.phone_number}</code>, авторизация отменена, повторите добавление ещё раз немного позже.</b>'
                            )
                            try:
                                await delete_2fa(await select_phone_queue(primary_id=write.id), proxy_data)
                            except:
                                pass
                            try:
                                if write.drop_bot_message_id:
                                    await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                            except:
                                pass
                            return
                    else:
                        change_password_status = False

                        if write.spamblock_status_check == 0:
                            try:
                                resp, resp2 = await asyncio.wait_for(send_message_for_check_spam(write=write, proxy=proxy_data), timeout=60)
                            except asyncio.TimeoutError:
                                logger.error(f'\n\n[app.py:send_message_for_check_spam] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                resp, resp2 = None, None
                            except:
                                resp, resp2 = None, None
                            logger.info(f'\n\n[app.py:send_message_for_check_spam] session_name: {write.session_name} | resp: {resp} | resp2: {resp2} | proxy: {proxy_data}')
                            if not resp and resp2 is not None:
                                if resp2 == 'spam_block':
                                    status = 11
                                    text = f'<b>⚠️ На аккаунте <code>{write.phone_number}</code> спамблок, проверьте статус вручную через @spambot и добавьте номер ещё раз когда аккаунт будет свободен от ограничений.</b>'
                                elif resp2 == 'send_message_for_check_spam_error':
                                    status = 37
                                    text = f'<b>⚠️ Не удалось проверить спамблок на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2 == 'not_auth':
                                    status = 31
                                    text = f'<b>⚠️ Слетела авторизация на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2.startswith('flood_wait'):
                                    status = 10
                                    text = f'<b>⚠️ На номере <code>{write.phone_number}</code> ограничение на выполнение действий, добавьте номер ещё раз через {resp2.split("|")[1]} сек.</b>'
                                elif resp2 == 'invalid_phone':
                                    status = 28
                                    text = f'<b>📵 Вы ввели неверный номер телефона <code>{write.phone_number}</code>, авторизация отменена.</b>'
                                elif resp2 == 'phone_banned':
                                    status = 26
                                    text = f'<b>⛔️ Номер телефона <code>{write.phone_number}</code> заблокирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'phone_unregistered':
                                    status = 29
                                    text = f'<b>❓ Номер телефона <code>{write.phone_number}</code> не зарегистрирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'password_needed':
                                    status = 4
                                    text = f'<b>🚫 На аккаунте <code>{write.phone_number}</code>установлен пароль, авторизация отменена.</b>'
                                elif resp2 == 'frozen_method_invalid':
                                    status = 41
                                    text = f'<b>⛔️ Аккаунт <code>{write.phone_number}</code> заморожен, авторизация отменена.</b>'
                                else:
                                    status = None
                                    text = None
                                if status and text:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.auth_proxy: proxy_data,
                                            PhoneQueue.last_check_at: datetime.now(),
                                            PhoneQueue.sent_sms_status: 1,
                                            PhoneQueue.spamblock_status_check: 2,
                                            PhoneQueue.status: status,
                                        }
                                    )
                                    await BotSendMessage(
                                        bot,
                                        chat_id=write.drop_id,
                                        text=text
                                    )
                                    try:
                                        if write.drop_bot_message_id:
                                            await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                    except:
                                        pass
                            else:
                                if resp and resp2:
                                    try:
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.spamblock_status_check: 1,
                                                PhoneQueue.last_check_at: datetime.now(),
                                            }
                                        )
                                    except:
                                        traceback.print_exc()
                                        try:
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.spamblock_status_check: 1,
                                                    PhoneQueue.last_check_at: datetime.now(),
                                                }
                                            )
                                        except:
                                            traceback.print_exc()
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.spamblock_status_check: 1,
                                                    PhoneQueue.last_check_at: datetime.now(),
                                                }
                                            )
                        
                        if write.shadowban_status_check == 0:
                            try:
                                resp, resp2 = await asyncio.wait_for(check_shadow_ban(write=write, proxy=proxy_data), timeout=60)
                            except asyncio.TimeoutError:
                                logger.error(f'\n\n[app.py:check_shadow_ban] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                resp, resp2 = None, None
                            except:
                                resp, resp2 = None, None
                            logger.info(f'\n\n[app.py:check_shadow_ban] session_name: {write.session_name} | resp: {resp} | resp2: {resp2} | proxy: {proxy_data}')
                            if not resp and resp2 is not None:
                                if resp2 == 'spam_block':
                                    status = 38
                                    text = f'<b>⚠️ На аккаунте <code>{write.phone_number}</code> теневой бан, проверьте вручную может ли аккаунт добавлять/искать новые контакты и добавьте номер ещё раз когда аккаунт будет свободен от ограничений.</b>'
                                elif resp2 == 'check_shadow_ban_error':
                                    status = 39
                                    text = f'<b>⚠️ На аккаунте <code>{write.phone_number}</code> теневой бан, проверьте вручную может ли аккаунт добавлять/искать новые контакты и добавьте номер ещё раз когда аккаунт будет свободен от ограничений.</b>'
                                    # text = f'<b>⚠️ Не удалось проверить теневой бан на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2 == 'not_auth':
                                    status = 31
                                    text = f'<b>⚠️ Слетела авторизация на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2.startswith('flood_wait'):
                                    status = 10
                                    text = f'<b>⚠️ На номере <code>{write.phone_number}</code> ограничение на выполнение действий, добавьте номер ещё раз через {resp2.split("|")[1]} сек.</b>'
                                elif resp2 == 'invalid_phone':
                                    status = 28
                                    text = f'<b>📵 Вы ввели неверный номер телефона <code>{write.phone_number}</code>, авторизация отменена.</b>'
                                elif resp2 == 'phone_banned':
                                    status = 26
                                    text = f'<b>⛔️ Номер телефона <code>{write.phone_number}</code> заблокирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'phone_unregistered':
                                    status = 29
                                    text = f'<b>❓ Номер телефона <code>{write.phone_number}</code> не зарегистрирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'password_needed':
                                    status = 4
                                    text = f'<b>🚫 На аккаунте <code>{write.phone_number}</code>установлен пароль, авторизация отменена.</b>'
                                elif resp2 == 'frozen_method_invalid':
                                    status = 41
                                    text = f'<b>⛔️ Аккаунт <code>{write.phone_number}</code> заморожен, авторизация отменена.</b>'
                                else:
                                    status = None
                                    text = None
                                if status and text:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.auth_proxy: proxy_data,
                                            PhoneQueue.last_check_at: datetime.now(),
                                            PhoneQueue.sent_sms_status: 1,
                                            PhoneQueue.shadowban_status_check: 2,
                                            PhoneQueue.status: status,
                                        }
                                    )
                                    await BotSendMessage(
                                        bot,
                                        chat_id=write.drop_id,
                                        text=text
                                    )
                                    try:
                                        if write.drop_bot_message_id:
                                            await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                    except:
                                        pass
                            else:
                                if resp and resp2:
                                    try:
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.shadowban_status_check: 1,
                                                PhoneQueue.last_check_at: datetime.now(),
                                            }
                                        )
                                    except:
                                        traceback.print_exc()
                                        try:
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.shadowban_status_check: 1,
                                                    PhoneQueue.last_check_at: datetime.now(),
                                                }
                                            )
                                        except:
                                            traceback.print_exc()
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.shadowban_status_check: 1,
                                                    PhoneQueue.last_check_at: datetime.now(),
                                                }
                                            )

                        write = await select_phone_queue(primary_id=write.id)
                        if write.spamblock_status_check == 1 and write.shadowban_status_check == 1:
                            change_password_status = True

                        if change_password_status:  
                            try:
                                resp, resp2 = await asyncio.wait_for(enable_2fa(write=write, proxy=proxy_data), timeout=60)
                            except asyncio.TimeoutError:
                                logger.error(f'\n\n[app.py:enable_2fa] session_name: {write.session_name} | TimeoutError | proxy: {proxy_data}')
                                resp, resp2 = None, None
                            except:
                                resp, resp2 = None, None
                            logger.info(f'\n\n[app.py:enable_2fa] session_name: {write.session_name} | resp: {resp} | resp2: {resp2} | proxy: {proxy_data}')
                            if not resp and resp2 is not None:
                                if resp2 == 'edit_2fa_error':
                                    status = 7
                                    text = f'<b>⚠️ Не удалось установить пароль на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2 == 'not_auth':
                                    status = 31
                                    text = f'<b>⚠️ Слетела авторизация на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.</b>'
                                elif resp2.startswith('flood_wait'):
                                    status = 10
                                    text = f'<b>⚠️ На номере <code>{write.phone_number}</code> ограничение на установку пароля, добавьте номер ещё раз через {resp2.split("|")[1]} сек.</b>'
                                elif resp2 == 'invalid_phone':
                                    status = 28
                                    text = f'<b>📵 Вы ввели неверный номер телефона <code>{write.phone_number}</code>, авторизация отменена.</b>'
                                elif resp2 == 'phone_banned':
                                    status = 26
                                    text = f'<b>⛔️ Номер телефона <code>{write.phone_number}</code> заблокирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'phone_unregistered':
                                    status = 29
                                    text = f'<b>❓ Номер телефона <code>{write.phone_number}</code> не зарегистрирован в телеграм, авторизация отменена.</b>'
                                elif resp2 == 'password_needed':
                                    status = 4
                                    text = f'<b>🚫 На аккаунте <code>{write.phone_number}</code>установлен пароль, авторизация отменена.</b>'
                                elif resp2 == 'frozen_method_invalid':
                                    status = 41
                                    text = f'<b>⛔️ Аккаунт <code>{write.phone_number}</code> заморожен, авторизация отменена.</b>'
                                else:
                                    status = None
                                    text = None
                                try:
                                    await delete_2fa(await select_phone_queue(primary_id=write.id), proxy_data)
                                except:
                                    pass
                                if status and text:
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.auth_proxy: proxy_data,
                                            PhoneQueue.last_check_at: datetime.now(),
                                            PhoneQueue.sent_sms_status: 1,
                                            PhoneQueue.status: status,
                                        }
                                    )
                                    await BotSendMessage(
                                        bot,
                                        chat_id=write.drop_id,
                                        text=text
                                    )
                                    try:
                                        if write.drop_bot_message_id:
                                            await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                    except:
                                        pass
                            else:
                                if resp and resp2:
                                    try:
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.status: 8,
                                                PhoneQueue.last_check_at: datetime.now(),
                                            }
                                        )
                                    except:
                                        traceback.print_exc()
                                        try:
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.status: 8,
                                                    PhoneQueue.last_check_at: datetime.now(),
                                                }
                                            )
                                        except:
                                            traceback.print_exc()
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.status: 8,
                                                    PhoneQueue.last_check_at: datetime.now(),
                                                }
                                            )
                                    response = await BotSendMessage(
                                        bot,
                                        chat_id=write.drop_id,
                                        text=(
                                            f'<b>✅ Пароль успешно установлен на <code>{write.phone_number}</code></b>'
                                            '\n<b>ℹ️ Исключите в устройствах все сессии кроме недавно вошедшей и выйдите из аккаунта.</b>'
                                            '\n<b>❗️ У вас есть 20 минут до отмены</b>'
                                        )
                                    )
                                    try:
                                        try:
                                            if write.drop_bot_message_id:
                                                await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                        except:
                                            pass
                                        if response:
                                            await update_phone_queue(
                                                primary_id=write.id,
                                                data={
                                                    PhoneQueue.drop_bot_message_id: response.message_id if response else None,
                                                }
                                            )
                                    except:
                                        pass


            elif write.status == 8:
                proxy_data = write.auth_proxy
                if proxy_data:
                    proxy_data = {"scheme": proxy_data['scheme'], "hostname": proxy_data['hostname'], "port": int(proxy_data['port']), "username": proxy_data['username'], "password": proxy_data['password']}
                if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                    proxy_data = await select_proxy_socks_5()
                    if proxy_data:
                        proxy_data = {'scheme': proxy_data.scheme, 'hostname': proxy_data.ip, 'port': int(proxy_data.port), 'username': proxy_data.login, 'password': proxy_data.password}
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        logger.error(f'[{write.id} > {write.phone_number}] pass: {write.password} > НЕТ ПРОКСИ ДЛЯ ПРОВЕРКИ СЕССИЙ')
                        if await different_time(write.last_check_at, 21):
                            await update_phone_queue(
                                primary_id=write.id,
                                data={
                                    PhoneQueue.status: 32,
                                }
                            )
                            await BotSendMessage(
                                bot,
                                chat_id=write.drop_id,
                                text=f'<b>❌ Не удалось авторизовать аккаунт <code>{write.phone_number}</code>, повторите добавление ещё раз немного позже.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                            )
                            try:
                                if write.drop_bot_message_id:
                                    await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                            except:
                                pass
                            try:
                                await delete_2fa(write, proxy_data)
                            except:
                                pass
                            return
                        else:
                            return
                if proxy_data:
                    if await different_time(write.last_check_at, 21):
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.status: 9,
                            }
                        )
                        await BotSendMessage(
                            bot,
                            chat_id=write.drop_id,
                            text=f'<b>❌ Не удалось авторизовать аккаунт <code>{write.phone_number}</code>, повторите добавление ещё раз немного позже.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                        )
                        try:
                            if write.drop_bot_message_id:
                                await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                        except:
                            pass
                        try:
                            await delete_2fa(write, proxy_data)
                        except:
                            pass
                        return
                    else:
                        try:
                            resp, resp2 = await asyncio.wait_for(check_sessions(write=write, proxy=proxy_data), timeout=60)
                        except asyncio.TimeoutError:
                            resp, resp2 = None, None
                        except:
                            resp, resp2 = None, None
                        logger.info(f'\n\n[app.py:check_sessions] session_name: {write.session_name} | resp: {resp} | resp2: {resp2} | proxy: {proxy_data}')
                        if not resp and resp2 is not None:
                            if resp2 == 'edit_2fa_error':
                                return
                            elif resp2 == 'not_auth':
                                status = 31
                                text = f'<b>⚠️ Слетела авторизация на <code>{write.phone_number}</code>, добавьте номер ещё раз немного позже.\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code></b>'
                            elif resp2.startswith('flood_wait'):
                                status = 10
                                text = f'<b>⚠️ На аккаунте <code>{write.phone_number}</code> ограничение от телеграм, добавьте номер ещё раз через {resp2.split("|")[1]} сек.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                            elif resp2 == 'invalid_phone':
                                status = 28
                                text = f'<b>📵 Вы ввели неверный номер телефона <code>{write.phone_number}</code>, авторизация отменена.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                            elif resp2 == 'phone_banned':
                                status = 26
                                text = f'<b>⛔️ Номер телефона <code>{write.phone_number}</code> заблокирован в телеграм, авторизация отменена.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                            elif resp2 == 'phone_unregistered':
                                status = 29
                                text = f'<b>❓ Номер телефона <code>{write.phone_number}</code> не зарегистрирован в телеграм, авторизация отменена.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                            elif resp2 == 'frozen_method_invalid':
                                status = 41
                                text = f'<b>⛔️ Аккаунт <code>{write.phone_number}</code> заморожен, авторизация отменена.</b>\n<b>🔑 Установленный пароль:</b> <code>{write.password}</code>'
                            else:
                                status = None
                                text = None
                            if status and text:
                                await update_phone_queue(
                                    primary_id=write.id,
                                    data={
                                        PhoneQueue.auth_proxy: proxy_data,
                                        PhoneQueue.last_check_at: datetime.now(),
                                        PhoneQueue.sent_sms_status: 1,
                                        PhoneQueue.status: status,
                                    }
                                )
                                await BotSendMessage(
                                    bot,
                                    chat_id=write.drop_id,
                                    text=text
                                )
                                try:
                                    if write.drop_bot_message_id:
                                        await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                except:
                                    pass
                        else:
                            if resp and resp2:
                                try:
                                    calc_amount = 0
                                    drop = await select_user(user_id=write.drop_id)
                                    if drop.calc_amount and drop.calc_amount > 0:
                                        calc_amount = drop.calc_amount
                                    elif bt.main_drop_calc_amount and bt.main_drop_calc_amount > 0:
                                        calc_amount = bt.main_drop_calc_amount
                                    await update_phone_queue(
                                        primary_id=write.id,
                                        data={
                                            PhoneQueue.confirmed_status: 1,
                                            PhoneQueue.status: 12,
                                            PhoneQueue.set_at: datetime.now(),
                                            PhoneQueue.payed_amount: calc_amount,
                                        }
                                    )
                                except:
                                    traceback.print_exc()
                                    try:
                                        calc_amount = 0
                                        drop = await select_user(user_id=write.drop_id)
                                        if drop.calc_amount and drop.calc_amount > 0:
                                            calc_amount = drop.calc_amount
                                        elif bt.main_drop_calc_amount and bt.main_drop_calc_amount > 0:
                                            calc_amount = bt.main_drop_calc_amount
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.confirmed_status: 1,
                                                PhoneQueue.status: 12,
                                                PhoneQueue.set_at: datetime.now(),
                                                PhoneQueue.payed_amount: calc_amount,
                                            }
                                        )
                                    except:
                                        traceback.print_exc()
                                        calc_amount = 0
                                        drop = await select_user(user_id=write.drop_id)
                                        if drop.calc_amount and drop.calc_amount > 0:
                                            calc_amount = drop.calc_amount
                                        elif bt.main_drop_calc_amount and bt.main_drop_calc_amount > 0:
                                            calc_amount = bt.main_drop_calc_amount
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.confirmed_status: 1,
                                                PhoneQueue.status: 12,
                                                PhoneQueue.set_at: datetime.now(),
                                                PhoneQueue.payed_amount: calc_amount,
                                            }
                                        )
                                await update_bot_setting(data={BotSetting.day_count_added: BotSetting.day_count_added + 1})
                                response = await BotSendMessage(
                                    bot,
                                    chat_id=write.drop_id,
                                    text=(
                                        f'<b>✅ Аккаунт <code>{write.phone_number}</code> успешно добавлен!</b>'
                                        f'\n<b>💵 Сумма покупки:</b> <code>{calc_amount:.2f}$</code>'
                                    )
                                )
                                try:
                                    try:
                                        if write.drop_bot_message_id:
                                            await BotDeleteMessage(bot, chat_id=write.drop_id, message_id=write.drop_bot_message_id)
                                    except:
                                        pass
                                    if response:
                                        await update_phone_queue(
                                            primary_id=write.id,
                                            data={
                                                PhoneQueue.drop_bot_message_id: response.message_id if response else None,
                                            }
                                        )
                                except:
                                    pass
                                return

        except Exception as e:
            logger.error(f"Error processing phone {write.id}: {str(e)}")
            raise
        finally:
            async with self.lock:
                if write.id in self.active_tasks:
                    del self.active_tasks[write.id]
                self.completed_ids.add(write.id)

    async def should_process_write(self, write_id: int) -> bool:
        async with self.lock:
            if write_id in self.active_tasks:
                return False
            if write_id in self.completed_ids:
                self.completed_ids.remove(write_id)
                return True
            return True

    async def start_task(self, write, bot):
        async with self.lock:
            if write.id in self.active_tasks:
                return
            
            task = asyncio.create_task(self.process_single_phone(write, bot))
            self.active_tasks[write.id] = task

    async def clean_completed_tasks(self):
        async with self.lock:
            completed = []
            for write_id, task in self.active_tasks.items():
                if task.done():
                    completed.append(write_id)
            
            for write_id in completed:
                del self.active_tasks[write_id]

    async def processing_phones(self, bot):
        processor = PhoneQueueProcessor()
        
        while True:
            try:
                await processor.clean_completed_tasks()
                
                writes = await select_phone_queues(statuses=[0,1,6,8])
                
                if writes:
                    logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] processing_phones: {len(writes)}')
                    
                    for write in writes:
                        if await processor.should_process_write(write.id):
                            await processor.start_task(write, bot)
                
            except Exception as e:
                logger.error(f"Error in main processing loop: {str(e)}")
                
            finally:
                await asyncio.sleep(5)































async def check_phones_5(bot):
    while True:
        try:
            writes = await select_phone_queues(statuses=[14])
            if writes:
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] check_phones_5: {len(writes)}')
                for write in writes:
                    bt = await select_bot_setting()
                    write = await select_phone_queue(primary_id=write.id)

                    if write.status == 14 and await different_time(write.updated_at, 2):
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.client_id: None,
                                PhoneQueue.group_id: None,
                                PhoneQueue.group_user_message_id: None,
                                PhoneQueue.status: 12,
                                PhoneQueue.updated_at: datetime.now(),
                                PhoneQueue.confirmed_at: None
                            }
                        )
                        await BotEditText(
                            bot,
                            chat_id=write.group_id,
                            message_id=write.group_bot_message_id,
                            text=f'<b>❌ Вы не ответили на запись с номером <code>{write.phone_number}</code>.</b>'
                        )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)


async def process_write(bot, write):
    try:
        bt = await select_bot_setting()
        write = await select_phone_queue(primary_id=write.id)

        if write.status == 15:
            mins = 5
            if await different_time(write.updated_at, mins):
                if write.last_auth_code is None:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.client_id: None,
                            PhoneQueue.group_id: None,
                            PhoneQueue.group_user_message_id: None,
                            PhoneQueue.status: 12,
                            PhoneQueue.updated_at: datetime.now(),
                            PhoneQueue.skip_count: PhoneQueue.skip_count + 1,
                            PhoneQueue.skip_group_id_1: write.skip_group_id_1 if write.skip_group_id_1 == write.group_id else write.group_id,
                            PhoneQueue.skip_group_id_2: write.group_id if not write.skip_group_id_2 else None
                        }
                    )
                    await BotEditText(
                        bot,
                        chat_id=write.group_id,
                        message_id=write.group_bot_message_id,
                        text=(
                            f'<b>⚠️ Не пришёл код:</b> <code>{write.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                            f'\n\n<b>❗️ Проверьте ваш IP на ограничения от телеграма и возьмите новую запись по команде /tg</b>'
                        ),
                        reply_markup=None
                    )
                    write = await select_phone_queue(primary_id=write.id)
                    if write.skip_count >= 2:
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.status: 22,
                                PhoneQueue.readded_at: datetime.now() + timedelta(hours=24)
                            }
                        )
                else:
                    group_info = await select_group(group_id=write.group_id)
                    if group_info and group_info.calc_amount and group_info.calc_amount > 0:
                        calc_amount = group_info.calc_amount
                    else:
                        calc_amount = bt.main_group_calc_amount
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.status: 17,
                            PhoneQueue.updated_at: datetime.now(),
                            PhoneQueue.buyed_at: datetime.now(),
                            PhoneQueue.buyed_amount: calc_amount,
                        }
                    )
                    await BotEditText(
                        bot,
                        chat_id=write.group_id,
                        message_id=write.group_bot_message_id,
                        text=(
                            f'<b>✅ Подтверждён:</b> <code>{write.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                            f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
                            f'\n<b>✉️ Код:</b> <code>{write.last_auth_code}</code>'
                            f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
                        ),
                        reply_markup=None
                    )
            else:
                if write.last_auth_code is not None and datetime.now() >= write.last_check_at:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.last_check_at: datetime.now() + timedelta(seconds=20),
                        }
                    )
                    await BotEditText(
                        bot,
                        chat_id=write.group_id,
                        message_id=write.group_bot_message_id,
                        text=(
                            f'<b>⏳ Получение кода:</b> <code>{write.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                            f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
                            f'\n<b>✉️ Код:</b> <code>{write.last_auth_code}</code>'
                            f'\n\n<b>❗️ Если код неверный, то отправьте его заново, сообщение автоматически обновляется до подтверждения. Номер действителен 5 минут с момента запроса.</b>'
                            f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
                        ),
                        reply_markup=None
                    )
                
                proxy_data = write.auth_proxy
                if proxy_data:
                    proxy_data = {"scheme": proxy_data['scheme'], "hostname": proxy_data['hostname'], "port": int(proxy_data['port']), "username": proxy_data['username'], "password": proxy_data['password']}
                if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                    proxy_data = await select_proxy_socks_5()
                    if proxy_data:
                        proxy_data = {'scheme': proxy_data.scheme, 'hostname': proxy_data.ip, 'port': int(proxy_data.port), 'username': proxy_data.login, 'password': proxy_data.password}
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        return False

                try:
                    resp, resp2 = await asyncio.wait_for(get_42777_code(write=write, proxy=proxy_data), timeout=10)
                except asyncio.TimeoutError:
                    resp, resp2 = None, None
                except:
                    resp, resp2 = None, None
                if resp and resp2:
                    if resp2 != write.last_auth_code:
                        await update_phone_queue(primary_id=write.id, data={PhoneQueue.last_auth_code: resp2})
                        await BotEditText(
                            bot,
                            chat_id=write.group_id,
                            message_id=write.group_bot_message_id,
                            text=(
                                f'<b>⏳ Получение кода:</b> <code>{write.phone_number}</code>'
                                f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                                f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
                                f'\n<b>✉️ Код:</b> <code>{resp2}</code>'
                                f'\n\n<b>❗️ Если код неверный, то отправьте его заново, сообщение автоматически обновляется до подтверждения. Номер действителен 5 минут с момента запроса.</b>'
                                f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
                            ),
                            reply_markup=None
                        )
    except Exception as e:
        traceback.print_exc()

async def process_write_with_limit(sem, bot, write):
    async with sem:
        await process_write(bot, write)

async def check_phones_6(bot):
    sem = asyncio.Semaphore(999)
    while True:
        try:
            writes = await select_phone_queues(statuses=[15])
            if writes:
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] check_phones_6: {len(writes)}')
                tasks = [process_write_with_limit(sem, bot, write) for write in writes]
                await asyncio.gather(*tasks)
        except Exception as e:
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)
                                

async def check_phones_7(bot):
    while True:
        try:
            writes = await select_phone_queues(statuses=[22])
            if writes:
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] check_phones_7: {len(writes)}')
                for write in writes:
                    bt = await select_bot_setting()
                    write = await select_phone_queue(primary_id=write.id)

                    if write.status == 22:
                        if datetime.now() > write.readded_at:
                            await update_phone_queue(
                                primary_id=write.id,
                                data={
                                    PhoneQueue.status: 12,
                                    PhoneQueue.skip_count: 0,
                                    PhoneQueue.skip_group_id_1: None,
                                    PhoneQueue.skip_group_id_2: None,
                                    PhoneQueue.updated_at: datetime.now()
                                }
                            )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)


async def send_message_with_retries(bot, user_id, text, max_attempts=6, delay=10):
    for attempt in range(max_attempts):
        resp = await BotSendMessage(
            bot, 
            chat_id=user_id, 
            text=text, 
            disable_web_page_preview=True
        )
        if resp:
            return True
        if attempt < max_attempts - 1:
            retry_delay = delay * (2 ** attempt)
            await asyncio.sleep(retry_delay)
    return False

async def auto_withdraw(bot):
    while True:
        try:
            bt = await select_bot_setting()
            if bt.auto_withdraw_status == 1 and bt.topic_withdraws_theme_id and bt.topic_failed_withdraws_theme_id:
                withdraws = await select_withdraws(withdraw_status=0)
                if withdraws:
                    for withdraw in withdraws:
                        withdraw = await select_withdraw(primary_id=withdraw.id)
                        if withdraw.withdraw_status == 0 and withdraw.amount and withdraw.writes and withdraw.phones:
                            user_id = withdraw.user_id
                            user_info = await select_user(user_id=user_id)
                            amount = withdraw.amount
                            amount = round(amount, 6)
                            writes = withdraw.writes
                            phones = withdraw.phones
                            # logger.info(user_id, amount, writes)
                            try:
                                response = await asyncio.wait_for(pyro_create_check(amount=amount), timeout=60)
                            except asyncio.TimeoutError:
                                response = None
                            except:
                                response = None
                            withdraw = await select_withdraw(primary_id=withdraw.id)
                            if withdraw.withdraw_status == 0:
                                logger.info(f'[{user_id}] {amount:.2f}$ | response: {response} | writes ({len(writes)}): {writes}')
                                if response is not None:
                                    if not response and withdraw.notify_status == 0:
                                        sent_response = await BotSendMessage(
                                            bot,
                                            chat_id=bt.topic_id,
                                            message_thread_id=bt.topic_failed_withdraws_theme_id,
                                            text=(
                                                f'<b>‼️ Недостаточный баланс для вывода средств!</b>'
                                                f'\n<b>├ ID:</b> <code>{user_id}</code>'
                                                f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
                                                f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
                                                f'\n<b>├ Сумма чека:</b> <code>{amount:.2f}$</code>'
                                                f'\n<b>└ Номера:</b> {", ".join([f"<code>{phone}</code>" for phone in phones])}'
                                            ),
                                            disable_web_page_preview=True
                                        )
                                        if sent_response:
                                            await update_withdraw(primary_id=withdraw.id, data={Withdraw.notify_status: 1})
                                    elif response:
                                        try:
                                            await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 1, Withdraw.withdraw_at: datetime.now()})
                                        except:
                                            await asyncio.sleep(5)
                                            try:
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 1, Withdraw.withdraw_at: datetime.now()})
                                            except:
                                                traceback.print_exc()
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 1, Withdraw.withdraw_at: datetime.now()})
                                        await asyncio.sleep(1)
                                        await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 1, Withdraw.withdraw_at: datetime.now()})
                                        withdraw = await select_withdraw(primary_id=withdraw.id)
                                        if withdraw.withdraw_status == 0:
                                            try:
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 1, Withdraw.withdraw_at: datetime.now()})
                                            except:
                                                traceback.print_exc()
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 1, Withdraw.withdraw_at: datetime.now()})
                                        await asyncio.sleep(1)
                                        withdraw = await select_withdraw(primary_id=withdraw.id)
                                        if withdraw.withdraw_status == 1:
                                            for write in writes:
                                                try:
                                                    await update_phone_queue(primary_id=write, data={PhoneQueue.withdraw_id: withdraw.id, PhoneQueue.withdraw_status: 1, PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_at: datetime.now()})
                                                except:
                                                    try:
                                                        await update_phone_queue(primary_id=write, data={PhoneQueue.withdraw_id: withdraw.id, PhoneQueue.withdraw_status: 1, PhoneQueue.pre_withdraw_status: 2, PhoneQueue.withdraw_at: datetime.now()})
                                                    except:
                                                        traceback.print_exc()

                                            check_text = (
                                                f'💸 <a href="http://t.me/send?start={response}">Чек</a> на <b>{amount:.2f}$</b> за {len(phones)} {await decline_number(len(phones))}'
                                                f'\n<b>└ Подтверждённые номера:</b> {", ".join([f"<code>{phone}</code>" for phone in phones])}'
                                            )
                                            success = await send_message_with_retries(bot, user_id, check_text)
                                            if not success:
                                                logger.error(f"Failed to send message to user {user_id} after 6 attempts")
                                                await BotSendMessage(
                                                    bot,
                                                    chat_id=bt.topic_id,
                                                    message_thread_id=bt.topic_withdraws_theme_id,
                                                    text=(
                                                        f'<b>✅ Вывод средств</b>'
                                                        f'\n<i>⚠️ Возможно что чек не дошёл до пользователя</i>'
                                                        f'\n<b>├ ID:</b> <code>{user_id}</code>'
                                                        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
                                                        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
                                                        f'\n<b>├ Сумма чека:</b> <code>{amount:.2f}$</code>'
                                                        f'\n<b>├ Чек:</b> http://t.me/send?start={response}'
                                                        f'\n<b>└ Номера:</b> {", ".join([f"<code>{phone}</code>" for phone in phones])}'
                                                    ),
                                                    disable_web_page_preview=True
                                                )
                                            else:
                                                await BotSendMessage(
                                                    bot,
                                                    chat_id=bt.topic_id,
                                                    message_thread_id=bt.topic_withdraws_theme_id,
                                                    text=(
                                                        f'<b>✅ Вывод средств</b>'
                                                        f'\n<b>├ ID:</b> <code>{user_id}</code>'
                                                        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
                                                        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
                                                        f'\n<b>├ Сумма чека:</b> <code>{amount:.2f}$</code>'
                                                        f'\n<b>├ Чек:</b> http://t.me/send?start={response}'
                                                        f'\n<b>└ Номера:</b> {", ".join([f"<code>{phone}</code>" for phone in phones])}'
                                                    ),
                                                    disable_web_page_preview=True
                                                )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(90)


async def process_single_write(write, bot, bt, semaphore):
    async with semaphore:
        try:
            # logger.info(f'Checker processing write: {write.phone_number} | {write.session_name}')
            write = await select_phone_queue(primary_id=write.id)
            if write.status not in [12, 22, 18]:
                return
            proxy_data = write.auth_proxy
            if proxy_data:
                proxy_data = {
                    "scheme": proxy_data['scheme'],
                    "hostname": proxy_data['hostname'],
                    "port": int(proxy_data['port']),
                    "username": proxy_data['username'],
                    "password": proxy_data['password']
                }
            if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                proxy_data = await select_proxy_socks_5()
                if proxy_data:
                    proxy_data = {
                        'scheme': proxy_data.scheme,
                        'hostname': proxy_data.ip,
                        'port': int(proxy_data.port),
                        'username': proxy_data.login,
                        'password': proxy_data.password
                    }
                if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                    return
            try:
                resp, resp2 = await asyncio.wait_for(
                    validate_session(write=write, proxy=proxy_data),
                    timeout=10
                )
            except (asyncio.TimeoutError, Exception):
                resp, resp2 = None, None
            if not resp and resp2 is not None:
                write = await select_phone_queue(primary_id=write.id)
                logger.info(f'Session invalidated: {write.phone_number} | {write.session_name}')
                await update_phone_queue(
                    primary_id=write.id,
                    data={
                        PhoneQueue.status: 24,
                        PhoneQueue.slet_at: datetime.now(),
                        PhoneQueue.slet_main_at: datetime.now(),
                    }
                )
                if write.status != 18:
                    await BotSendMessage(
                        bot,
                        chat_id=bt.topic_id,
                        message_thread_id=bt.topic_phones_theme_id,
                        text=await get_nevalid_session_info(user_info=await select_user(user_id=write.drop_id), write=write),
                        reply_markup=multi_2_kb(
                            text='🚷 Заблокировать', callback_data=f'TOPIC_US|{write.id}|BAN', 
                            text_back='☑️ Разблокировать', callback_data_back=f'TOPIC_US|{write.id}|UNBAN', 
                        ),
                        disable_web_page_preview=True
                    )
            else:
                try:
                    resp, resp2 = await asyncio.wait_for(
                        account_is_frozen_status(write=write, proxy=proxy_data),
                        timeout=10
                    )
                except (asyncio.TimeoutError, Exception):
                    resp, resp2 = None, None
                if resp and resp2:
                    logger.info(f'ACC_FROZEN: {write.phone_number} | {write.session_name}')
                    write = await select_phone_queue(primary_id=write.id)
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.status: 42,
                            PhoneQueue.slet_at: datetime.now(),
                            PhoneQueue.slet_main_at: datetime.now(),
                        }
                    )
                    if write.status != 18:
                        await BotSendMessage(
                            bot,
                            chat_id=bt.topic_id,
                            message_thread_id=bt.topic_frozen_theme_id,
                            text=await get_frozen_session_info(user_info=await select_user(user_id=write.drop_id), write=write),
                            reply_markup=multi_2_kb(
                                text='🚷 Заблокировать', callback_data=f'TOPIC_US|{write.id}|BAN', 
                                text_back='☑️ Разблокировать', callback_data_back=f'TOPIC_US|{write.id}|UNBAN', 
                            ),
                            disable_web_page_preview=True
                        )
                
        except Exception as e:
            logger.error(f"Error processing write {write.id}: {str(e)}")
            traceback.print_exc()

async def accounts_checker(bot):
    semaphore = Semaphore(29)
    while True:
        try:
            logger.info('accounts_checker waiting cycle')
            # await asyncio.sleep(900)
            bt = await select_bot_setting()
            if not (bt.accounts_checker_status == 1 and bt.topic_phones_theme_id):
                continue
            writes = []
            writes_1 = await select_phone_queues(statuses=[12, 22], sort_desc=True)
            if writes_1:
                writes += writes_1
            writes_2 = await select_phone_queues(status=18, alive_status_in=[2,3,9], sort_desc=True)
            if writes_2:
                writes += writes_2
            if not writes:
                continue
            tasks = [
                asyncio.create_task(process_single_write(write, bot, bt, semaphore))
                for write in writes
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in accounts_checker: {str(e)}")
            traceback.print_exc()
        finally:
            await asyncio.sleep(900)


async def autoload_proxy(bot):
    while True:
        try:
            bt = await select_bot_setting()
            if bt.autoload_proxy_status == 1 and bt.topic_autoload_proxy and bt.proxy_api_token:
                if len(await select_proxy_socks_5s()) < 100:
                    proxies = None
                    dop_text = ''
                    scheme = 'SOCKS5'
                    try:
                        api = ProxySaleAPI(bt.proxy_api_token)
                        russian_proxies = await api.get_russian_proxies()
                        print(f"Найдено прокси: {len(russian_proxies)}")
                        if russian_proxies:
                            proxy = russian_proxies[0]
                            try:
                                dop_text = (
                                    f"🌍 <b>{proxy['title']}</b>"
                                    f"\n🆔 <code>{proxy['id']}</code>"
                                    f"\n🔑 <code>{proxy['login']}:{proxy['password']}</code>"
                                    f"\n🔄 <b>rotation per request <code>{proxy['rotation']}</code> seconds</b>"
                                )
                            except:
                                traceback.print_exc()
                            proxies = await api.download_proxy_details(proxy_id=proxy['id'], proto=scheme)
                            print(f"proxies: {len(proxies)}")
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Произошла ошибка: {str(e)}")
                    # print(proxies)
                    if proxies and ';' in str(proxies):
                        valid = 0
                        not_valid = 0
                        not_valid_list = []
                        added = 0
                        skip = 0
                        error = 0
                        proxies = str(proxies).split('\n')
                        
                        response = await BotSendMessage(
                            bot,
                            chat_id=bt.topic_id,
                            message_thread_id=bt.topic_autoload_proxy,
                            text=(
                                f'<b>⏳ Проверка <code>{len(proxies)}</code> {scheme}..</b>'
                            )
                        )
                        if response:
                            update_interval = 15
                            count = 0
                            for proxy in proxies:
                                try:
                                    if proxy:
                                        proxy = proxy.split(';')
                                        hostname = proxy[0]
                                        port = proxy[1]
                                        username = proxy[2]
                                        password = proxy[3]
                                        # print(proxy, hostname, port, username, password)
                                        if hostname and port and username and password:
                                            port = int(port)
                                            if await select_proxy_socks_5(scheme=scheme.lower(), login=username, password=password, ip=hostname, port=port):
                                                skip += 1
                                            else:
                                                try:
                                                    valid_status = await check_proxy(proxy={'scheme': scheme.lower(), 'hostname': hostname, 'port': port, 'username': username, 'password': password})
                                                except:
                                                    valid_status = False
                                                if valid_status:
                                                    valid += 1
                                                else:
                                                    not_valid += 1
                                                    not_valid_list.append(f"{username}:{password}@{hostname}:{port}")
                                                if valid_status:
                                                    await add_proxy_socks_5(scheme=scheme.lower(), login=username, password=password, ip=hostname, port=port)
                                                    added += 1
                                        else:
                                            error += 1
                                    else:
                                        error += 1
                                    count += 1
                                    if count % update_interval == 0:
                                        await BotEditText(
                                            bot,
                                            chat_id=bt.topic_id,
                                            message_id=response.message_id,
                                            text=(
                                                f'<b>⏳ Проверка <code>{len(proxies)}</code> {scheme} прокси..</b>'
                                                f'\n<b>├ Уже в базе:</b> <code>{skip}/{len(proxies)}</code>'
                                                f'\n<b>├ Добавлено:</b> <code>{added}/{len(proxies)}</code>'
                                                f'\n<b>└ Невалидных:</b> <code>{not_valid}/{added}</code>'
                                                f'\n\n{dop_text}'
                                            )
                                        )
                                except:
                                    traceback.print_exc()
                        if response:
                            await BotEditText(
                                bot,
                                chat_id=bt.topic_id,
                                message_id=response.message_id,
                                text=(
                                    f'<b>✅ {scheme}</b>'
                                    f'\n<b>├ Уже в базе:</b> <code>{skip}/{len(proxies)}</code>'
                                    f'\n<b>├ Добавлено:</b> <code>{added}/{len(proxies)}</code>'
                                    f'\n<b>└ Невалидных:</b> <code>{not_valid}/{added}</code>'
                                    f'\n\n{dop_text}'
                                )
                            )

            if bt.autoload_proxy_status == 1 and bt.topic_autoload_proxy and bt.converter_proxy_api_token:
                if len(await select_converter_proxy_socks_5s()) < 100:
                    proxies = None
                    dop_text = ''
                    scheme = 'SOCKS5'
                    try:
                        api = ProxySaleAPI(bt.converter_proxy_api_token)
                        russian_proxies = await api.get_russian_proxies()
                        print(f"Найдено прокси: {len(russian_proxies)}")
                        if russian_proxies:
                            proxy = russian_proxies[0]
                            try:
                                dop_text = (
                                    f"🌍 <b>{proxy['title']}</b>"
                                    f"\n🆔 <code>{proxy['id']}</code>"
                                    f"\n🔑 <code>{proxy['login']}:{proxy['password']}</code>"
                                    f"\n🔄 <b>rotation per request <code>{proxy['rotation']}</code> seconds</b>"
                                )
                            except:
                                traceback.print_exc()
                            proxies = await api.download_proxy_details(proxy_id=proxy['id'], proto=scheme)
                            print(f"proxies: {len(proxies)}")
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Произошла ошибка: {str(e)}")
                    # print(proxies)
                    if proxies and ';' in str(proxies):
                        valid = 0
                        not_valid = 0
                        not_valid_list = []
                        added = 0
                        skip = 0
                        error = 0
                        proxies = str(proxies).split('\n')
                        
                        response = await BotSendMessage(
                            bot,
                            chat_id=bt.topic_id,
                            message_thread_id=bt.topic_autoload_proxy,
                            text=(
                                f'<b>🔁⏳ Проверка <code>{len(proxies)}</code> {scheme} прокси для конвертера..</b>'
                            )
                        )
                        if response:
                            update_interval = 15
                            count = 0
                            for proxy in proxies:
                                try:
                                    if proxy:
                                        proxy = proxy.split(';')
                                        hostname = proxy[0]
                                        port = proxy[1]
                                        username = proxy[2]
                                        password = proxy[3]
                                        # print(proxy, hostname, port, username, password)
                                        if hostname and port and username and password:
                                            port = int(port)
                                            if await select_converter_proxy_socks_5(scheme=scheme.lower(), login=username, password=password, ip=hostname, port=port):
                                                skip += 1
                                            else:
                                                try:
                                                    valid_status = await check_proxy(proxy={'scheme': scheme.lower(), 'hostname': hostname, 'port': port, 'username': username, 'password': password})
                                                except:
                                                    valid_status = False
                                                if valid_status:
                                                    valid += 1
                                                else:
                                                    not_valid += 1
                                                    not_valid_list.append(f"{username}:{password}@{hostname}:{port}")
                                                if valid_status:
                                                    await add_converter_proxy_socks_5(scheme=scheme.lower(), login=username, password=password, ip=hostname, port=port)
                                                    added += 1
                                        else:
                                            error += 1
                                    else:
                                        error += 1
                                    count += 1
                                    if count % update_interval == 0:
                                        await BotEditText(
                                            bot,
                                            chat_id=bt.topic_id,
                                            message_id=response.message_id,
                                            text=(
                                                f'<b>🔁⏳ Проверка <code>{len(proxies)}</code> {scheme} прокси для конвертера..</b>'
                                                f'\n<b>├ Уже в базе:</b> <code>{skip}/{len(proxies)}</code>'
                                                f'\n<b>├ Добавлено:</b> <code>{added}/{len(proxies)}</code>'
                                                f'\n<b>└ Невалидных:</b> <code>{not_valid}/{added}</code>'
                                                f'\n\n{dop_text}'
                                            )
                                        )
                                except:
                                    traceback.print_exc()
                        if response:
                            await BotEditText(
                                bot,
                                chat_id=bt.topic_id,
                                message_id=response.message_id,
                                text=(
                                    f'<b>🔁✅ {scheme}</b>'
                                    f'\n<b>├ Уже в базе:</b> <code>{skip}/{len(proxies)}</code>'
                                    f'\n<b>├ Добавлено:</b> <code>{added}/{len(proxies)}</code>'
                                    f'\n<b>└ Невалидных:</b> <code>{not_valid}/{added}</code>'
                                    f'\n\n{dop_text}'
                                )
                            )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(7)

async def proxy_checker(bot):
    while True:
        try:
            bt = await select_bot_setting()
            if bt.proxy_checker_status == 1 and bt.topic_errors_proxy_theme_id:
                writes = await select_proxy_socks_5s()
                if writes:
                    for write in writes:
                        write = await select_proxy_socks_5(scheme=write.scheme, ip=write.ip, port=write.port, login=write.login, password=write.password)
                        if write:
                            if write.count_errors >= 30:
                                await delete_proxy_socks_5(scheme=write.scheme, ip=write.ip, port=write.port, login=write.login, password=write.password)
                                await BotSendMessage(
                                    bot,
                                    chat_id=bt.topic_id,
                                    message_thread_id=bt.topic_errors_proxy_theme_id,
                                    text=(
                                        f'<b>❌ Невалидные прокси</b>'
                                        f'\n<b>├ Тип прокси:</b> <code>{write.scheme}</code>'
                                        f'\n<b>└ Данные прокси:</b> <code>{write.login}:{write.password}@{write.ip}:{write.port}</code>'
                                    ),
                                    disable_web_page_preview=True
                                )
                            else:
                                response = await check_proxy(proxy={'scheme': write.scheme, 'hostname': write.ip, 'port': int(write.port), 'username': write.login, 'password': write.password})
                                if response:
                                    await update_proxy_socks_5(
                                        scheme=write.scheme, 
                                        ip=write.ip, 
                                        port=write.port, 
                                        login=write.login, 
                                        password=write.password,
                                        data={
                                            ProxySocks5.count_errors: 0
                                        }
                                    )
                                else:
                                    await update_proxy_socks_5(
                                        scheme=write.scheme, 
                                        ip=write.ip, 
                                        port=write.port, 
                                        login=write.login, 
                                        password=write.password,
                                        data={
                                            ProxySocks5.count_errors: ProxySocks5.count_errors + 1
                                        }
                                    )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(60)


async def proxy_checker_2(bot):
    while True:
        try:
            bt = await select_bot_setting()
            if bt.proxy_checker_status == 1 and bt.topic_errors_proxy_theme_id:
                writes = await select_converter_proxy_socks_5s()
                if writes:
                    for write in writes:
                        write = await select_converter_proxy_socks_5(scheme=write.scheme, ip=write.ip, port=write.port, login=write.login, password=write.password)
                        if write:
                            if write.count_errors >= 60:
                                await delete_converter_proxy_socks_5(scheme=write.scheme, ip=write.ip, port=write.port, login=write.login, password=write.password)
                                await BotSendMessage(
                                    bot,
                                    chat_id=bt.topic_id,
                                    message_thread_id=bt.topic_errors_proxy_theme_id,
                                    text=(
                                        f'<b>❌ Невалидные прокси для конвертации</b>'
                                        f'\n<b>├ Тип прокси:</b> <code>{write.scheme}</code>'
                                        f'\n<b>└ Данные прокси:</b> <code>{write.login}:{write.password}@{write.ip}:{write.port}</code>'
                                    ),
                                    disable_web_page_preview=True
                                )
                            else:
                                response = await check_proxy(proxy={'scheme': write.scheme, 'hostname': write.ip, 'port': int(write.port), 'username': write.login, 'password': write.password})
                                if response:
                                    await update_converter_proxy_socks_5(
                                        scheme=write.scheme, 
                                        ip=write.ip, 
                                        port=write.port, 
                                        login=write.login, 
                                        password=write.password,
                                        data={
                                            ProxySocks5.count_errors: 0
                                        }
                                    )
                                else:
                                    await update_converter_proxy_socks_5(
                                        scheme=write.scheme, 
                                        ip=write.ip, 
                                        port=write.port, 
                                        login=write.login, 
                                        password=write.password,
                                        data={
                                            ProxySocks5.count_errors: ProxySocks5.count_errors + 1
                                        }
                                    )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(60)


async def scheduler_text(bot):
    while True:
        current_time = datetime.now()
        writes = await select_scheduler_groups(current_time=current_time)
        # logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER WAITING..')
        if writes:
            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER COUNT: {len(writes)}')
            for write in writes:
                unique_id = write.unique_id
                group_id = write.group_id
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER | unique_id: {unique_id} | group_id: {group_id}')
                text = await select_scheduler_text(unique_id=unique_id)
                if write.period:
                    period = write.period
                else:
                    period = 0
                if write.period_minutes:
                    period_minutes = write.period_minutes
                else:
                    period_minutes = 0

                await update_scheduler_group(
                    unique_id=unique_id,
                    group_id=group_id,
                    period=period,
                    period_minutes=period_minutes,
                    data={
                        SchedulerGroup.last_sended_at: datetime.now(),
                        SchedulerGroup.next_sended_at: datetime.now() + timedelta(hours=period) + timedelta(minutes=period_minutes)
                    }
                )
                if text:
                    group_info = await select_group(group_id=group_id)
                    if group_info and group_info.work_status == 1:
                        if period != 0 or period_minutes != 0:
                            if text.file_name:
                                await BotSendPhoto(
                                    bot,
                                    group_id,
                                    FSInputFile(f'temp/{text.file_name}'),
                                    caption=text.text
                                )
                            else:
                                await BotSendMessage(
                                    bot,
                                    chat_id=group_id,
                                    text=text.text,
                                    disable_web_page_preview=text.disable_web_page_preview
                                )
            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER COMPLETED!')
        await asyncio.sleep(15)


async def scheduler_bot(bot):
    while True:
        current_time = datetime.now()
        writes = await select_scheduler_bots(current_time=current_time)
        # logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER WAITING..')
        if writes:
            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER BOT COUNT: {len(writes)}')
            for write in writes:
                unique_id = write.unique_id
                text = await select_scheduler_text(unique_id=unique_id)
                if write.period:
                    period = write.period
                else:
                    period = 0
                if write.period_minutes:
                    period_minutes = write.period_minutes
                else:
                    period_minutes = 0
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER BOT | unique_id: {unique_id} | period: {period_minutes} | period_minutes: {period_minutes}')

                await update_scheduler_bot(
                    unique_id=unique_id,
                    period=period,
                    period_minutes=period_minutes,
                    data={
                        SchedulerBot.last_sended_at: datetime.now(),
                        SchedulerBot.next_sended_at: datetime.now() + timedelta(hours=period) + timedelta(minutes=period_minutes)
                    }
                )
                if text and write.enable_status == 1:
                    if period != 0 or period_minutes != 0:
                        writes = await select_users()
                        try:
                            if write.ids_remove and write.ids_remove != [] and write.ids_remove != ' ' and str(write.ids_remove) != '[]' and str(write.ids_remove) != ' ':
                                ids_remove = ast.literal_eval(write.ids_remove)
                            else:
                                ids_remove = []
                        except Exception as e:
                            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER BOT ERROR: {e} | unique_id: {unique_id} | period: {period_minutes} | period_minutes: {period_minutes}')
                            traceback.print_exc()
                            ids_remove = []

                        users_to_send = []
                        for w in writes:
                            user_id = w.user_id
                            if user_id in ids_remove or str(user_id) in ids_remove or str(user_id) in str(ids_remove):
                                pass
                            else:
                                users_to_send.append(user_id)

                        if users_to_send:
                            counter = 0 
                            for user_id in users_to_send:
                                if user_id != ADMIN_ID:
                                    try:
                                        if text.file_name:
                                            await BotSendPhoto(
                                                bot,
                                                user_id,
                                                FSInputFile(f'temp/{text.file_name}'),
                                                caption=text.text
                                            )
                                        else:
                                            await BotSendMessage(
                                                bot,
                                                chat_id=user_id,
                                                text=text.text,
                                                disable_web_page_preview=text.disable_web_page_preview
                                            )
                                        counter += 1
                                        if counter % 20 == 0:
                                            await asyncio.sleep(5)
                                    except Exception as e:
                                        pass
            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] SCHEDULER COMPLETED!')
        await asyncio.sleep(15)


async def scheduler(bot):
    set_time = '00:00'
    while True:
        current_time = datetime.now().strftime("%H:%M")
        if set_time == current_time:
            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] RESET TABLES..')
            await update_user(
                data={
                    User.added_count: 0
                }
            )
            await update_bot_setting(
                data={
                    BotSetting.day_count_added: 0,
                    BotSetting.day_count_sended: 0
                }
            )
            logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] RESET COMPLETED!')
        await asyncio.sleep(30)


async def set_default_commands(bot):
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='ℹ️ Главное меню'),
            BotCommand(command='/shop', description='🛒 Товары'),
            BotCommand(command='/tg', description='📱 Получить номер'),
        ]
    )



async def set_default_commands2(bot):
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='ℹ️ Главное меню'),
            BotCommand(command='/tg', description='📱 Получить телеграм'),
            BotCommand(command='/slet', description='🚫 Слёт'),
            BotCommand(command='/stats', description='📊 Статистика (для группы)'),
            BotCommand(command='/gadd', description='➕ Добавить группу'),
            BotCommand(command='/gdel', description='➖ Удалить группу'),
        ]
    )

async def otlega_checker(bot):
    while True:
        try:
            otlega_groups = await select_many_records(OtlegaGroup)
            if otlega_groups:
                for otg in otlega_groups:
                    if otg.refill_accounts_status == 0 and otg.skip_updates_status == 0:
                        total_accounts = len(await select_many_records(PhoneQueue, otlega_unique_id=otg.unique_id, status_in=[12, 14, 15], sort_asc='set_at'))
                        if total_accounts < otg.count_accounts:
                            need_count = otg.count_accounts - total_accounts
                            await update_record(
                                PhoneQueue, 
                                update_limit_count=need_count, 
                                otlega_unique_id_is_none=True,
                                status=12, 
                                data={
                                    PhoneQueue.otlega_unique_id: otg.unique_id,
                                    PhoneQueue.otlega_count_days: otg.count_days
                                }
                            )
                            total_accounts = len(await select_many_records(PhoneQueue, otlega_unique_id=otg.unique_id, status_in=[12, 14, 15]))
                            if total_accounts >= otg.count_accounts:
                                await update_record(OtlegaGroup, unique_id=otg.unique_id, data={OtlegaGroup.skip_updates_status: 1})
                    elif otg.refill_accounts_status == 1:
                        total_accounts = len(await select_many_records(PhoneQueue, otlega_unique_id=otg.unique_id, status_in=[12, 14, 15]))
                        if total_accounts < otg.count_accounts:
                            need_count = otg.count_accounts - total_accounts
                            await update_record(
                                PhoneQueue, 
                                update_limit_count=need_count, 
                                otlega_unique_id_is_none=True,
                                status=12, 
                                data={
                                    PhoneQueue.otlega_unique_id: otg.unique_id,
                                    PhoneQueue.otlega_count_days: otg.count_days
                                }
                            )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(45)


async def autokick_check(bot):
    while True:
        bt = await select_bot_setting()
        if bt.auto_kick_group_status == 1 and bt.op_group_id:
            for user in await select_users(is_banned=1):
                if user and user.is_banned == 1 and user.role != 'admin' and user.user_id != ADMIN_ID:
                    # print(f'1user: {user.user_id}')
                    await asyncio.sleep(0.11)
                    try:
                        member = await BotGetChatMember(bot, chat_id=bt.op_group_id, user_id=user.user_id)
                        if member and hasattr(member, 'status') and member.status == 'member':
                            print(f'1user kicked: {user.user_id}')
                            await BotBanChatMember(bot, chat_id=bt.op_group_id, user_id=user.user_id, revoke_messages=False)
                            await BotUnBanChatMember(bot, chat_id=bt.op_group_id, user_id=user.user_id)
                    except Exception as e:
                        if 'PARTICIPANT_ID_INVALID' in str(e):
                            pass
                        else:
                            traceback.print_exc()
            for user in await select_users(not_role='drop'):
                if user and user.role != 'drop' and user.role != 'admin' and user.user_id != ADMIN_ID:
                    # print(f'1user: {user.user_id}')
                    await asyncio.sleep(0.11)
                    try:
                        member = await BotGetChatMember(bot, chat_id=bt.op_group_id, user_id=user.user_id)
                        if member and hasattr(member, 'status') and member.status == 'member':
                            print(f'1user kicked: {user.user_id}')
                            await BotBanChatMember(bot, chat_id=bt.op_group_id, user_id=user.user_id, revoke_messages=False)
                            await BotUnBanChatMember(bot, chat_id=bt.op_group_id, user_id=user.user_id)
                    except Exception as e:
                        if 'PARTICIPANT_ID_INVALID' in str(e):
                            pass
                        else:
                            traceback.print_exc()
        await asyncio.sleep(120)


async def first_bot():
    dp1 = Dispatcher(storage=MemoryStorage())
    dp1.update.outer_middleware(UpdateUserDataMiddleware())
    dp1.update.outer_middleware(ManualCheckMiddleware())
    dp1.update.outer_middleware(SubCheckMiddleware())

    dp1.include_routers(
        clear_notify_router,
        admin_router,
        topic_router,
        client_group_router,
        client_private_router,
        drop_router,
        drop_or_client_router,
    )
    
    bot_settings = {'session': AiohttpSession(), 'parse_mode': 'HTML'}
    bot1 = Bot(token=BOT_TOKEN, **bot_settings)
    await bot1.delete_webhook()
    await set_default_commands2(bot1)
    logger.info('First bot is running!')
    
    tasks = []
    try:
        main_tasks = asyncio.gather(
            autokick_check(bot1),
            otlega_checker(bot1),
            scheduler(bot1),
            scheduler_text(bot1),
            scheduler_bot(bot1),
            check_phones_5(bot1),
            check_phones_6(bot1),
            check_phones_7(bot1),
            auto_withdraw(bot1),
            accounts_checker(bot1),
            proxy_checker(bot1),
            proxy_checker_2(bot1),
            autoload_proxy(bot1),
            pslet_check(bot1),
            alive_check(bot1),
            PhoneQueueProcessor().processing_phones(bot1),
            dp1.start_polling(bot1, allowed_updates=allowed_updates)
        )
        tasks.append(main_tasks)
        await main_tasks
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)




async def usdt_processing(bot):
    await asyncio.sleep(5)
    while True:
        bt = await select_bot_setting()
        response_json = None
        try:
            timestamp_24h_ago = int((time.time() - 24 * 60 * 60) * 1000)
            # timestamp_24h_ago = int((time.time()) - 10 * 24 * 60 * 60) * 1000 # 10d
            async with aiohttp.ClientSession() as session:
                url = f'https://api.trongrid.io/v1/accounts/{bt.usdt_address}/transactions/trc20'
                params = {
                    'only_to': 'true',
                    'min_timestamp': timestamp_24h_ago,
                    'limit': 100
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        response_json = await response.json()
        except Exception:
            traceback.print_exc()
        # print(response_json)
        if response_json:
            transfers_data = {}
            data = response_json.get("data", [])
            for transfer in data:
                if (transfer.get("token_info", {}).get("symbol") == "USDT" and 
                    transfer.get("type") == "Transfer"):
                    transaction_id = transfer.get("transaction_id")
                    is_confirmed = await check_transaction_confirmation(transaction_id, session=None)
                    if not is_confirmed:
                        print(f"Transaction {transaction_id} is not confirmed yet, skipping")
                        continue
                    token_decimals = transfer.get("token_info", {}).get("decimals", 6)
                    raw_amount = int(transfer.get("value", "0"))
                    amount = raw_amount / (10 ** token_decimals)
                    transfers_data[amount] = {
                        "from_address": transfer.get("from"),
                        "transaction_hash": transaction_id,
                        "timestamp": int(transfer.get("block_timestamp", 0) / 1000),
                        "amount": amount,
                    }
            # print(f'\ntransfers_data: {transfers_data}')
            if transfers_data:
                print(f'\ntransfers_data: {transfers_data}')
                writes = await select_payments(status=0)
                if writes:
                    for write in writes:
                        response = transfers_data.get(write.amount_usdt, None)
                        if response:
                            transaction_hash = response.get('transaction_hash')
                            if transaction_hash:
                                if not await select_payment(transaction_hash=transaction_hash, status=1):
                                    await update_payment(
                                        primary_id=write.id,
                                        data={
                                            Payment.from_address: response.get("from_address"),
                                            Payment.transaction_hash: response.get("transaction_hash"),
                                            Payment.status: 1,
                                            Payment.timestamp: response.get("timestamp"),
                                            Payment.updated_at: datetime.now(),
                                        }
                                    )
                                    await update_user(user_id=write.user_id, data={User.balance: User.balance + write.amount_usdt})
                                    await BotSendMessage(bot, chat_id=write.user_id, text=f'<b>💸 Ваш баланс пополнен на {famount(write.amount_usdt)}$</b>')
                                    if write.message_notify_id:
                                        await BotEditText(
                                            bot,
                                            chat_id=write.user_id,
                                            message_id=write.message_notify_id,
                                            text=f'<b>✅ Транзакция на сумму <code>{famount(write.amount_usdt)}</code> <code>USDT</code> оплачена.</b>'
                                        )
                                    user = await select_user(user_id=write.user_id)
                                    bot_settings = {"session": bot.session}
                                    aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                                    await BotSendMessage(
                                        aio_bot,
                                        chat_id=bt.topic_id,
                                        message_thread_id=bt.topic_payments_theme_id,
                                        text=(
                                            f'<b>✅ Пополнение на {famount(write.amount_usdt)} USDT</b>'
                                            f'\n<b>├ ID:</b> <code>{write.user_id}</code>'
                                            f'\n<b>├ Имя:</b> <code>{html.quote(user.fullname)}</code>'
                                            f'\n<b>├ Логин:</b> {f"@{user.username}" if user.username else "<code>отсутствует</code>"}'
                                            f'\n<b>├ Регистрация:</b> <code>{user.registered_at.strftime("%d.%m.%Y г. в %H:%M")}</code>'
                                            f'\n<b>├ С адреса:</b> <code>{response.get("from_address")}</code>'
                                            f'\n<b>├ На адрес:</b> <code>{write.usdt_address}</code>'
                                            f'\n<b>├ Время:</b> <code>{datetime.fromtimestamp(int(response.get("timestamp"))).strftime("%d.%m.%Y %H:%M") if response.get("timestamp") else "отсутствует"}</code>'
                                            f'\n<b>├ Хэш:</b> <code>{response.get("transaction_hash")}</code>'
                                            f'\n<b>└ Ссылка:</b> https://tronscan.org/#/transaction/{response.get("transaction_hash")}'
                                            f'\n\n#id{write.user_id}\n#{response.get("from_address")}\n#{write.usdt_address}\n#{response.get("transaction_hash")}'
                                        ),
                                        disable_web_page_preview=True
                                    )
                                    continue
                        if await different_time(write.added_at, 1500):
                            if (await select_payment(primary_id=write.id)).status == 0:
                                await update_payment(
                                    primary_id=write.id,
                                    data={
                                        Payment.status: 2,
                                        Payment.updated_at: datetime.now(),
                                    }
                                )
                                await BotEditText(
                                    bot,
                                    chat_id=write.user_id,
                                    message_id=write.message_notify_id,
                                    text=f'<b>❌ Транзакция на сумму <code>{famount(write.amount_usdt)}</code> <code>USDT</code> отменена.</b>'
                                )
        await asyncio.sleep(10)

async def check_transaction_confirmation(tx_id, session=None):
    if not tx_id:
        return False
    should_close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        should_close_session = True
    try:
        url = 'https://api.trongrid.io/wallet/gettransactioninfobyid'
        data = {"value": tx_id}
        async with session.post(url, json=data) as response:
            if response.status == 200:
                tx_info = await response.json()
                if "blockNumber" in tx_info and "blockTimeStamp" in tx_info:
                    if tx_info.get("receipt", {}).get("result", "SUCCESS") == "SUCCESS":
                        async with session.post('https://api.trongrid.io/wallet/getnowblock') as latest_response:
                            if latest_response.status == 200:
                                latest_block = await latest_response.json()
                                current_block = latest_block.get("block_header", {}).get("raw_data", {}).get("number", 0)
                                tx_block = tx_info.get("blockNumber", 0)
                                confirmations = current_block - tx_block
                                print(f"Transaction {tx_id}: {confirmations} confirmations")
                                return confirmations >= 19
            else:
                print(f"result: {response.status}")
    except Exception as e:
        print(f"Error checking transaction confirmation: {str(e)}")
    finally:
        if should_close_session:
            await session.close()
    return False



# async def usdt_processing(bot):
#     await asyncio.sleep(5)
#     while True:
#         bt = await select_bot_setting()
#         response_json = None
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(
#                     f'https://apilist.tronscanapi.com/api/token_trc20/transfers?start=0&toAddress={bt.usdt_address}&start_timestamp={(int(time.time()) - 24 * 60 * 60) * 1000}&end_timestamp=&confirm=true&filterTokenValue=1',
#                     headers={'TRON-PRO-API-KEY': '7d449661-5d8f-424d-9b22-1b055f0104a9'}) as response:
#                     if response.status == 200:
#                         response_json = await response.json()
#         except:
#             traceback.print_exc()
#         print(response_json)
#         if response_json:
#             transfers_data = {}
#             total = response_json.get("total", 0)
#             if int(total) >= 0:
#                 transfers = response_json.get("token_transfers")
#                 for transfer in transfers:
#                     token_info = transfer.get("tokenInfo", {})
#                     if (token_info.get("tokenAbbr") == "USDT" and token_info.get("tokenType") == "trc20"):
#                         amount = int(transfer.get("quant", 0)) / (10 ** 6)
#                         # quant = transfer.get("quant", 0)
#                         # amount = Decimal(quant) / Decimal('1000000')
#                         # amount = amount.quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
#                         transfers_data[amount] = {
#                             "from_address": transfer.get("from_address"),
#                             "transaction_hash": transfer.get("transaction_id"),
#                             "timestamp": int(transfer.get("block_ts", 0) / 1000),
#                             "amount": amount,
#                         }
#             print(f'\ntransfers_data: {transfers_data}')
#             if transfers_data:
#                 writes = await select_payments(status=0)
#                 if writes:
#                     for write in writes:
#                         # print(f'Decimal(write.amount_usdt): {Decimal(write.amount_usdt)}')
#                         response = transfers_data.get(write.amount_usdt, None)
#                         # print(response)
#                         if response:
#                             transaction_hash = response.get('transaction_hash')
#                             if transaction_hash:
#                                 if not await select_payment(transaction_hash=transaction_hash, status=1):
#                                     await update_payment(
#                                         primary_id=write.id,
#                                         data={
#                                             Payment.from_address: response.get("from_address"),
#                                             Payment.transaction_hash: response.get("transaction_hash"),
#                                             Payment.status: 1,
#                                             Payment.timestamp: response.get("timestamp"),
#                                             Payment.updated_at: datetime.now(),
#                                         }
#                                     )
#                                     await update_user(user_id=write.user_id, data={User.balance: User.balance + write.amount_usdt})
#                                     await BotSendMessage(bot, chat_id=write.user_id, text=f'<b>💸 Ваш баланс пополнен на {famount(write.amount_usdt)}$</b>')
#                                     if write.message_notify_id:
#                                         await BotEditText(
#                                             bot,
#                                             chat_id=write.user_id,
#                                             message_id=write.message_notify_id,
#                                             text=f'<b>✅ Транзакция на сумму <code>{write.amount_usdt}</code> <code>USDT</code> оплачена.</b>'
#                                         )
#                                     user = await select_user(user_id=write.user_id)
#                                         abot_settings = {"session": bot.session}
#                                         aaio_bot = Bot(token=BOT_TOKEN, **bot_settings)
#                                         aawait BotSendMessage(
#                                         aio_bot,
#                                         chat_id=bt.topic_id,
#                                         message_thread_id=bt.topic_payments_theme_id,
#                                         text=(
#                                             f'<b>✅ Пополнение на {write.amount_usdt} USDT</b>'
#                                             f'\n<b>├ ID:</b> <code>{write.user_id}</code>'
#                                             f'\n<b>├ Имя:</b> <code>{html.quote(user.fullname)}</code>'
#                                             f'\n<b>├ Логин:</b> {f"@{user.username}" if user.username else "<code>отсутствует</code>"}'
#                                             f'\n<b>├ Регистрация:</b> <code>{user.registered_at.strftime("%d.%m.%Y г. в %H:%M")}</code>'
#                                             f'\n<b>├ С адреса:</b> <code>{response.get("from_address")}</code>'
#                                             f'\n<b>├ На адрес:</b> <code>{write.usdt_address}</code>'
#                                             f'\n<b>├ Сумма USDT:</b> <code>{write.amount_usdt:.6f}</code>'
#                                             f'\n<b>├ Курс обмена:</b> <code>{bt.usdt_currency}</code> <code>RUB</code>'
#                                             f'\n<b>├ Время:</b> <code>{datetime.fromtimestamp(int(response.get("timestamp"))).strftime("%d.%m.%Y %H:%M") if response.get("timestamp") else "отсутствует"}</code>'
#                                             f'\n<b>├ Хэш:</b> <code>{response.get("transaction_hash")}</code>'
#                                             f'\n<b>└ Ссылка:</b> https://tronscan.org/#/transaction/{response.get("transaction_hash")}'
#                                             f'\n\n#id{write.user_id}\n#{response.get("from_address")}\n#{write.usdt_address}\n#{response.get("transaction_hash")}'
#                                         ),
#                                         disable_web_page_preview=True
#                                     )
#                                     continue
#                         # if await different_time(write.added_at, bt.usdt_waiting):
#                         # либо этот метод со стаусом, либо ниже спустя время
#                         #     if write.message_notify_id:
#                         #         await BotEditText(
#                         #             bot,
#                         #             chat_id=write.user_id,
#                         #             message_id=write.message_notify_id,
#                         #             text=f'<b>❌ Транзакция на сумму <code>{write.amount_usdt}</code> <code>USDT</code> отменена.</b>'
#                         #         )
#                         if await different_time(write.added_at, 1500):
#                             if (await select_payment(primary_id=write.id)).status == 0:
#                                 await update_payment(
#                                     primary_id=write.id,
#                                     data={
#                                         Payment.status: 2,
#                                         Payment.updated_at: datetime.now(),
#                                     }
#                                 )
#                                 await BotEditText(
#                                     bot,
#                                     chat_id=write.user_id,
#                                     message_id=write.message_notify_id,
#                                     text=f'<b>❌ Транзакция на сумму <code>{write.amount_usdt}</code> <code>USDT</code> отменена.</b>'
#                                 )
#         await asyncio.sleep(10)

async def cryptobot_payments_check_writes(bot):
    await asyncio.sleep(10)
    while True:
        writes = await select_cryptobot_payments(status=0)
        if writes:
            for write in writes:
                if await different_time(write.added_at, 300):
                    await update_cryptobot_payment(
                        primary_id=write.id,
                        data={
                            Payment.status: 2,
                            Payment.updated_at: datetime.now(),
                        }
                    )
                    bot_settings = {"session": bot.session}
                    aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                    await BotSendMessage(
                        aio_bot,
                        chat_id=write.user_id,
                        reply_to_message_id=write.message_notify_id,
                        allow_sending_without_reply=True,
                        text=f'<b>❌ Транзакция на сумму <code>{famount(write.amount_usdt)}</code> <code>USDT</code> отменена.</b>'
                    )
        await asyncio.sleep(90)


async def cryptobot_payments_check_bills(bot):
    await asyncio.sleep(10)
    while True:
        await asyncio.sleep(random.randint(59, 118))
        try:
            count_messages = 0
            async for message in pyro_client_second.get_chat_history('me'):
                # print(message)
                count_messages += 1
                if count_messages % 1000 == 0:
                    print(f"{count_messages} messages. waiting..")
                    await asyncio.sleep(30)
                # print(count_messages)
                if message:
                    try:
                        message_text = message.text
                    except:
                        message_text = None
                    if message_text and 'Оплачен' in message_text and 'Счёт' in message_text:
                        # print(message)
                        message_text = message.text.html
                        # print(message_text)
                        if message_text and '<a href="http://t.me/CryptoBot?start=' in message_text:
                            message_text = message_text.split('<a href="http://t.me/CryptoBot?start=')[1]
                            invoice_hash = message_text.split('">')[0]
                            if invoice_hash:
                                # print(invoice_hash)
                                payment = await select_cryptobot_payment(transaction_hash=invoice_hash)
                                if payment and payment.status != 1:
                                    if payment.invoice_type == 0:
                                        bt = await select_bot_setting()
                                        user = await select_user(user_id=payment.user_id)
                                        await update_cryptobot_payment(transaction_hash=invoice_hash, data={CryptoBotPayment.status: 1, CryptoBotPayment.updated_at: datetime.now()})
                                        await update_user(user_id=payment.user_id, data={User.balance: User.balance + payment.amount_usdt})
                                        await BotSendMessage(bot, chat_id=payment.user_id, text=f'<b>💸 Ваш баланс пополнен на {famount(payment.amount_usdt)}$</b>')
                                        if payment.message_notify_id:
                                            await BotEditText(
                                                bot,
                                                chat_id=payment.user_id,
                                                message_id=payment.message_notify_id,
                                                text=f'<b>✅ Транзакция на сумму <code>{famount(payment.amount_usdt)}</code> <code>USDT</code> оплачена.</b>'
                                            )
                                        bot_settings = {"session": bot.session}
                                        aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                                        await BotSendMessage(
                                            aio_bot,
                                            chat_id=bt.topic_id,
                                            message_thread_id=bt.topic_cryptobot_payments_theme_id,
                                            text=(
                                                f'<b>✅ Пополнение на {famount(payment.amount_usdt)} USDT</b>'
                                                f'\n<b>├ ID:</b> <code>{payment.user_id}</code>'
                                                f'\n<b>├ Имя:</b> <code>{html.quote(user.fullname)}</code>'
                                                f'\n<b>├ Логин:</b> {f"@{user.username}" if user.username else "<code>отсутствует</code>"}'
                                                f'\n<b>├ Регистрация:</b> <code>{user.registered_at.strftime("%d.%m.%Y г. в %H:%M")}</code>'
                                                f'\n<b>├ Хэш:</b> <code>{payment.transaction_hash}</code>'
                                                f'\n<b>└ Ссылка:</b> <code>https://t.me/CryptoBot?start={payment.transaction_hash}</code>'
                                                f'\n\n#id{payment.user_id}'
                                            )
                                        )
                                    elif payment.invoice_type == 1:
                                        await update_user(user_id=payment.user_id, data={User.is_banned: 0, User.auto_ban_status: 0, User.phones_added_ban_expired_at: None})
                                        await update_cryptobot_payment(transaction_hash=invoice_hash, data={CryptoBotPayment.status: 1, CryptoBotPayment.updated_at: datetime.now()})
                                        unban_write = await select_one_record(UnbanWrite, sql_id=payment.id)
                                        if unban_write and unban_write.writes:
                                            for sql_id in unban_write.writes:
                                                await update_record(
                                                    PhoneQueue, 
                                                    id=sql_id, 
                                                    data={
                                                        PhoneQueue.updated_at: datetime.now(),
                                                        PhoneQueue.unlocked_at: datetime.now(),
                                                        PhoneQueue.unlocked_amount: PhoneQueue.payed_amount,
                                                        PhoneQueue.unban_month_status: 1
                                                    }
                                                )
                                        bt = await select_bot_setting()
                                        user = await select_user(user_id=payment.user_id)
                                        bot_settings = {"session": bot.session}
                                        aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                                        await BotSendMessage(aio_bot, chat_id=payment.user_id, text=f'<b>✅ Ваш аккаунт разблокирован</b>')
                                        if payment.message_notify_id:
                                            await BotEditText(
                                                aio_bot,
                                                chat_id=payment.user_id,
                                                message_id=payment.message_notify_id,
                                                text=f'<b>✅ Транзакция на сумму <code>{famount(payment.amount_usdt)}</code> <code>USDT</code> оплачена.</b>'
                                            )
                                        await BotSendMessage(
                                            aio_bot,
                                            chat_id=bt.topic_id,
                                            message_thread_id=bt.topic_cryptobot_payments_theme_id,
                                            text=(
                                                f'<b>✅🔗 Разблокировака аккаунта за {famount(payment.amount_usdt)} USDT</b>'
                                                f'\n<b>├ ID:</b> <code>{payment.user_id}</code>'
                                                f'\n<b>├ Имя:</b> <code>{html.quote(user.fullname)}</code>'
                                                f'\n<b>├ Логин:</b> {f"@{user.username}" if user.username else "<code>отсутствует</code>"}'
                                                f'\n<b>├ Регистрация:</b> <code>{user.registered_at.strftime("%d.%m.%Y г. в %H:%M")}</code>'
                                                f'\n<b>├ Хэш:</b> <code>{payment.transaction_hash}</code>'
                                                f'\n<b>└ Ссылка:</b> <code>https://t.me/CryptoBot?start={payment.transaction_hash}</code>'
                                                f'\n\n#id{payment.user_id}'
                                            )
                                        )
        except:
            traceback.print_exc()


async def check_catalog_take_phones():
    while True:
        try:
            writes = await select_phone_queues(statuses=[35])
            if writes:
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] check_catalog_take_phones: {len(writes)}')
                for write in writes:
                    write = await select_phone_queue(primary_id=write.id)
                    if write.status == 35 and await different_time(write.updated_at, 5):
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.client_id: None,
                                PhoneQueue.group_id: None,
                                PhoneQueue.group_user_message_id: None,
                                PhoneQueue.status: 18 if write.alive_status in [2,3,9] else 12,
                                PhoneQueue.updated_at: datetime.now(),
                            }
                        )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)



async def process_write_check_catalog_take_sms_phones(bot, write):
    try:
        write = await select_phone_queue(primary_id=write.id)
        if write.status == 36:
            mins = 5
            if await different_time(write.updated_at, mins):
                if write.last_auth_code is None:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.client_id: None,
                            PhoneQueue.group_id: None,
                            PhoneQueue.group_user_message_id: None,
                            PhoneQueue.status: 18 if write.alive_status in [2,3,9] else 12,
                            PhoneQueue.updated_at: datetime.now(),
                            PhoneQueue.skip_count: PhoneQueue.skip_count + 1
                        }
                    )
                    await update_user(user_id=write.client_id, data={User.balance: User.balance + write.buyed_amount})
                    await BotEditText(
                        bot,
                        chat_id=write.group_id if write.group_id else write.client_id,
                        message_id=write.group_bot_message_id,
                        text=(
                            f'<b>⚠️ Не пришёл код:</b> <code>{write.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                            f'\n\n<b>❗️ Проверьте ваш IP на ограничения от телеграма и возьмите новую запись по команде /tg</b>'
                        ),
                        reply_markup=None
                    )
                    write = await select_phone_queue(primary_id=write.id)
                    if write.skip_count >= 2:
                        await update_phone_queue(
                            primary_id=write.id,
                            data={
                                PhoneQueue.status: 22,
                                PhoneQueue.readded_at: datetime.now() + timedelta(hours=24)
                            }
                        )
                else:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.status: 17,
                            PhoneQueue.buyed_at: datetime.now(),
                            PhoneQueue.updated_at: datetime.now(),
                        }
                    )
                    await add_record(Archive, user_id=write.client_id, group_id=write.group_id, group_user_id=write.group_user_id, amount=write.buyed_amount, count_accounts=1, pack_id=write.pack_id, added_at=datetime.now())
                    await BotEditText(
                        bot,
                        chat_id=write.group_id if write.group_id else write.client_id,
                        message_id=write.group_bot_message_id,
                        text=(
                            f'<b>✅ Код получен:</b> <code>{write.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                            f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
                            f'\n<b>✉️ Код:</b> <code>{write.last_auth_code}</code>'
                        ),
                        # reply_markup=await multi_new_kb(text='🗄 Получить .session', callback_data=f'PACK|GET|SESSION|{write.pack_id}')
                    )
            else:
                if write.last_auth_code is not None and datetime.now() >= write.last_check_at:
                    await update_phone_queue(
                        primary_id=write.id,
                        data={
                            PhoneQueue.last_check_at: datetime.now() + timedelta(seconds=20),
                        }
                    )
                    await BotEditText(
                        bot,
                        chat_id=write.group_id if write.group_id else write.client_id,
                        message_id=write.group_bot_message_id,
                        text=(
                            f'<b>⏳ Получение кода:</b> <code>{write.phone_number}</code>'
                            f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                            f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
                            f'\n<b>✉️ Код:</b> <code>{write.last_auth_code}</code>'
                            f'\n\n<b>❗️ Если код неверный, то отправьте его заново, сообщение автоматически обновляется до подтверждения. Номер действителен 5 минут с момента запроса.</b>'
                        ),
                        # reply_markup=await multi_new_kb(text='🗄 Получить .session', callback_data=f'PACK|GET|SESSION|{write.pack_id}')
                    )
                proxy_data = write.auth_proxy
                if proxy_data:
                    proxy_data = {"scheme": proxy_data['scheme'], "hostname": proxy_data['hostname'], "port": int(proxy_data['port']), "username": proxy_data['username'], "password": proxy_data['password']}
                if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                    proxy_data = await select_proxy_socks_5()
                    if proxy_data:
                        proxy_data = {'scheme': proxy_data.scheme, 'hostname': proxy_data.ip, 'port': int(proxy_data.port), 'username': proxy_data.login, 'password': proxy_data.password}
                    if not proxy_data or (proxy_data and not await check_proxy(proxy=proxy_data)):
                        return False
                try:
                    resp, resp2 = await asyncio.wait_for(get_42777_code(write=write, proxy=proxy_data), timeout=10)
                except asyncio.TimeoutError:
                    resp, resp2 = None, None
                except:
                    resp, resp2 = None, None
                if resp and resp2:
                    if resp2 != write.last_auth_code:
                        await update_phone_queue(primary_id=write.id, data={PhoneQueue.last_auth_code: resp2})
                        await BotEditText(
                            bot,
                            chat_id=write.group_id if write.group_id else write.client_id,
                            message_id=write.group_bot_message_id,
                            text=(
                                f'<b>⏳ Получение кода:</b> <code>{write.phone_number}</code>'
                                f"{f'{chr(10)}<b>🕒 Отлега:</b> <code>{write.otlega_count_days} {await decline_day(write.otlega_count_days)}</code>' if write.otlega_count_days else ''}"
                                f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
                                f'\n<b>✉️ Код:</b> <code>{resp2}</code>'
                                f'\n\n<b>❗️ Если код неверный, то отправьте его заново, сообщение автоматически обновляется до подтверждения. Номер действителен 5 минут с момента запроса.</b>'
                            ),
                            # reply_markup=await multi_new_kb(text='🗄 Получить .session', callback_data=f'PACK|GET|SESSION|{write.pack_id}')
                        )
    except Exception as e:
        traceback.print_exc()

async def proccess_check_catalog_take_sms_phones(sem, bot, write):
    async with sem:
        await process_write_check_catalog_take_sms_phones(bot, write)

async def check_catalog_take_sms_phones(bot):
    sem = asyncio.Semaphore(999)
    while True:
        try:
            writes = await select_phone_queues(statuses=[36])
            if writes:
                logger.info(f'[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] check_catalog_take_sms_phones: {len(writes)}')
                tasks = [proccess_check_catalog_take_sms_phones(sem, bot, write) for write in writes]
                await asyncio.gather(*tasks)
        except Exception as e:
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)


async def client_withdraw(bot):
    while True:
        try:
            bt = await select_bot_setting()
            if bt.auto_withdraw_status == 1 and bt.topic_withdraws_theme_id and bt.topic_failed_withdraws_theme_id:
                withdraws = await select_withdraws(withdraw_status=10)
                if withdraws:
                    for withdraw in withdraws:
                        withdraw = await select_withdraw(primary_id=withdraw.id)
                        if withdraw.withdraw_status == 10 and withdraw.amount:
                            user_id = withdraw.user_id
                            user_info = await select_user(user_id=user_id)
                            amount = withdraw.amount
                            amount = round(amount, 6)
                            # logger.info(user_id, amount)
                            try:
                                response = await asyncio.wait_for(pyro_create_check(amount=amount), timeout=60)
                            except asyncio.TimeoutError:
                                response = None
                            except:
                                response = None
                            withdraw = await select_withdraw(primary_id=withdraw.id)
                            if withdraw.withdraw_status == 10:
                                logger.info(f'[{user_id}] {amount:.2f}$ | response: {response}')
                                if response is not None:
                                    if not response and withdraw.notify_status == 0:
                                        bot_settings = {"session": bot.session}
                                        aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                                        sent_response = await BotSendMessage(
                                            aio_bot,
                                            chat_id=bt.topic_id,
                                            message_thread_id=bt.topic_failed_withdraws_theme_id,
                                            text=(
                                                f'<b>‼️ Недостаточный баланс для вывода средств по рефке клиентского бота!</b>'
                                                f'\n<b>├ ID:</b> <code>{user_id}</code>'
                                                f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
                                                f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
                                                f'\n<b>└ Сумма чека:</b> <code>{amount:.2f}$</code>'
                                            ),
                                            disable_web_page_preview=True
                                        )
                                        if sent_response:
                                            await update_withdraw(primary_id=withdraw.id, data={Withdraw.notify_status: 1})
                                    elif response:
                                        try:
                                            await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 11, Withdraw.withdraw_at: datetime.now()})
                                        except:
                                            await asyncio.sleep(5)
                                            try:
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 11, Withdraw.withdraw_at: datetime.now()})
                                            except:
                                                traceback.print_exc()
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 11, Withdraw.withdraw_at: datetime.now()})
                                        await asyncio.sleep(1)
                                        await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 11, Withdraw.withdraw_at: datetime.now()})
                                        withdraw = await select_withdraw(primary_id=withdraw.id)
                                        if withdraw.withdraw_status == 10:
                                            try:
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 11, Withdraw.withdraw_at: datetime.now()})
                                            except:
                                                traceback.print_exc()
                                                await update_withdraw(primary_id=withdraw.id, data={Withdraw.check_id: response, Withdraw.withdraw_status: 11, Withdraw.withdraw_at: datetime.now()})
                                        await asyncio.sleep(1)
                                        withdraw = await select_withdraw(primary_id=withdraw.id)
                                        if withdraw.withdraw_status == 11:
                                            check_text = (
                                                f'💸 <a href="http://t.me/send?start={response}">Чек</a> на <b>{amount:.2f}$</b>'
                                            )
                                            success = await send_message_with_retries(bot, user_id, check_text)
                                            if not success:
                                                logger.error(f"Failed to send message to user {user_id} after 6 attempts")
                                                bot_settings = {"session": bot.session}
                                                aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                                                await BotSendMessage(
                                                    aio_bot,
                                                    chat_id=bt.topic_id,
                                                    message_thread_id=bt.topic_withdraws_theme_id,
                                                    text=(
                                                        f'<b>✅ Вывод средств по рефке клиентского бота</b>'
                                                        f'\n<i>⚠️ Возможно что чек не дошёл до пользователя</i>'
                                                        f'\n<b>├ ID:</b> <code>{user_id}</code>'
                                                        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
                                                        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
                                                        f'\n<b>├ Сумма чека:</b> <code>{amount:.2f}$</code>'
                                                        f'\n<b>└ Чек:</b> http://t.me/send?start={response}'
                                                    ),
                                                    disable_web_page_preview=True
                                                )
                                            else:
                                                bot_settings = {"session": bot.session}
                                                aio_bot = Bot(token=BOT_TOKEN, **bot_settings)
                                                await BotSendMessage(
                                                    aio_bot,
                                                    chat_id=bt.topic_id,
                                                    message_thread_id=bt.topic_withdraws_theme_id,
                                                    text=(
                                                        f'<b>✅ Вывод средств по рефке клиентского бота</b>'
                                                        f'\n<b>├ ID:</b> <code>{user_id}</code>'
                                                        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
                                                        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
                                                        f'\n<b>├ Сумма чека:</b> <code>{amount:.2f}$</code>'
                                                        f'\n<b>└ Чек:</b> http://t.me/send?start={response}'
                                                    ),
                                                    disable_web_page_preview=True
                                                )
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(90)


async def cryptobot_withdraw_money():
    await asyncio.sleep(10)
    while True:
        await asyncio.sleep(random.randint(1700, 2000))
        # await asyncio.sleep(10)
        bt = await select_bot_setting()
        if bt.cryptobot_main_invoice_url:
            invoice_hash = bt.cryptobot_main_invoice_url
            await pay_main_bill_link(invoice_hash=invoice_hash)


async def second_bot():
    dp2 = Dispatcher(storage=MemoryStorage())
    dp2.update.outer_middleware(UpdateUserDataMiddleware())
    dp2.update.outer_middleware(ClientsSubCheckMiddleware())
    
    dp2.include_routers(
        clients_group_router,
        clients_private_router,
    )
    
    bot_settings = {'session': AiohttpSession(), 'parse_mode': 'HTML'}
    bot2 = Bot(token=SECOND_BOT_TOKEN, **bot_settings)
    await bot2.delete_webhook()
    await set_default_commands(bot2)
    logger.info('Second bot is running!')
    tasks = []
    try:
        main_tasks = asyncio.gather(
            check_catalog_take_sms_phones(bot2),
            check_catalog_take_phones(),
            usdt_processing(bot2),
            cryptobot_payments_check_writes(bot2),
            cryptobot_payments_check_bills(bot2),
            client_withdraw(bot2),
            cryptobot_withdraw_money(),
            dp2.start_polling(bot2, allowed_updates=allowed_updates)
        )
        tasks.append(main_tasks)
        await main_tasks
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

async def start_pyro_main():
    await pyro_client.start()
    await pyro_client.stop()

async def start_pyro_second():
    await pyro_client_second.start()

async def run_all():
    await create_base()
    if not await select_bot_setting():
        await add_bot_setting()
   # await start_pyro_main() #
    await asyncio.gather(
        first_bot(),
        second_bot(),
        start_pyro_second(),
    )

if __name__ == "__main__":
    with suppress(KeyboardInterrupt, StopIteration):
        asyncio.run(run_all())