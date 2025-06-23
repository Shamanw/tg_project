import os
import re
import pytz
import time
import json
import random
import string
import shutil
import aiohttp
import zipfile
import pathlib
import rarfile 
import py7zr
import asyncio
import traceback

from aiogram import html
from aiogram.exceptions import TelegramRetryAfter

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from TGConvertor.manager import SessionManager, API
from python_socks._errors import ProxyError


from aiohttp import ClientSession, ClientConnectionError, ClientSSLError, ClientError, http_exceptions
from aiohttp_socks import ProxyConnector, ProxyError, ProxyConnectionError
# from python_socks._errors import ProxyConnectionError

from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

from telethon.errors import (
    FloodWaitError, 
    PhoneNumberInvalidError, SessionPasswordNeededError,
    PhoneNumberBannedError, PhoneNumberUnoccupiedError
)


from aiohttp import ClientConnectionError, ClientSSLError, ClientError
from aiohttp_socks import ProxyError, ProxyConnectionError, ProxyConnector
from python_socks._errors import ProxyError
from python_socks import ProxyTimeoutError



from keyboards.inline.misc_kb import *

from database.commands.main import *
from database.commands.users import *
from database.commands.groups import *
from database.commands.payments import *
from database.commands.cryptobot_payments import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *

from utils.additionally_bot import *

from config import *

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired, FloodWait, RPCError, AuthKeyUnregistered
from pyrogram.raw.functions.account import GetAuthorizations
from pyrogram.raw.types import EmailVerifyPurposeLoginSetup, EmailVerificationCode
from pyrogram.errors import EmailUnconfirmed

clients = {}


allowed_updates = [
    'message',
    'edited_message',
    'callback_query',
    # 'inline_query',
    # 'chosen_inline_result',
    'chat_member',
    'channel_post',
    'edited_channel_post',
    # 'shipping_query',
    # 'pre_checkout_query',
    # 'poll',
    # 'poll_answer',
    'my_chat_member',
    'chat_member',
    'chat_join_request',
    # 'message_reaction',
    # 'message_reaction_count',
    'chat_boost',
    'removed_chat_boost',
    'error',
]



archive_types = {
    "A_ALL": {
        "title": "<b>✅ В пулле</b>", 
        "status_in": [12],
        "set_at": True,
    },
    "A_WIOUT": {
        "title": "<b>✔️  В пулле без подгрупп</b>", 
        "status_in": [12],
        "otlega_unique_id_is_none": True,
        "set_at": True,
    },
    "A_DEF": {
        "title": "<b>✅ В пулле (ℹ️ Основной бот)</b>", 
        "status_in": [12],
        "client_bot": 0,
        "set_at": True,
    },
    "A_CLIENT": {
        "title": "<b>✅ В пулле (🤖 Клиентский бот)</b>", 
        "status_in": [12],
        "client_bot": 1,
        "set_at": True,
    },
    "SLET": {
        "title": "<b>💢 Слетевшие</b>", 
        "status_in": [18],
        "slet_at": True,
    },
    "DEL": {
        "title": "<b>🗑 Удалённые</b>", 
        "status_in": [19,20,21],
        "deleted_at": True,
    },
    "NOT_VALID": {
        "title": "<b>☠️ Невалидные</b>", 
        "status_in": [23, 24],
        "slet_at": True,
    },
    "FROZEN": {
        "title": "<b>❄️ Замороженные</b>", 
        "status_in": [42],
        "slet_at": True,
    },
    "NOT_SMS": {
        "title": "<b>✉️ Не приходит смс</b>", 
        "status_in": [22],
        "added_at": True,
    },
    "PHONES": {
        "title": "<b>📱 Все номера</b>", 
        "added_at": True,
    },
    "PAYED": {
        "title": "<b>💵 Оплаченные</b>", 
        "payed_amount_is_not_none": True,
        "set_at": True,
    },
    "BUYED": {
        "title": "<b>💷 Выданные</b>", 
        "status_in": [17],
        "buyed_at": True,
    },
    "AUTH": {
        "title": "<b>✍️ На авторизации</b>", 
        "status_in": [0, 1, 6, 8],
        "added_at": True,
    },
}











async def is_auto_withdrawal_enabled():
    moscow_tz = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(moscow_tz).time()
    
    if current_time.hour >= 0 and current_time.hour < 9:
        return False
    return True


async def get_time_at_period(type=None, r_all=False):
	types = {
		'today': 'сегодня',
		'yesterday': 'вчера',
		'beforeyesterday': 'позавчера',
		'week': 'неделю',
		'month': 'месяц',
		'previousmonth': 'предыдущий месяц',
	}
	if r_all:
		return [[key, value] for key, value in types.items()]
	else:
		return types.get(type, 'всё время')


async def check_tron_transaction(tx_hash, usdt_address):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}') as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('contractRet') == 'SUCCESS':
                        # print(data)
                        to_address = data.get('trc20TransferInfo', [{}])[0].get('to_address')
                        from_address = data.get('trc20TransferInfo', [{}])[0].get('from_address')
                        amount_str = data.get('trc20TransferInfo', [{}])[0].get('amount_str')
                        decimals = data.get('trc20TransferInfo', [{}])[0].get('decimals')
                        token_name = data.get('trc20TransferInfo', [{}])[0].get('symbol')
                        timestamp = data.get('timestamp')
                        if amount_str is not None and decimals is not None:
                           amount = int(amount_str) / (10 ** decimals)
                           amount = f"{amount:.{decimals}f}".rstrip('0').rstrip('.')
                        else:
                            amount = None
                        print(to_address, from_address, amount, token_name, timestamp)
                        if to_address == usdt_address:
                            if token_name == 'USDT':
                                return {
                                    "status": "success",
                                    "message": None,
                                    "from_address": from_address,
                                    "to_address": to_address,
                                    "token_name": token_name,
                                    "amount": amount,
                                    "timestamp": timestamp
                                }
                            else:
                                return {
                                    "status": "error",
                                    "to_address": to_address,
                                    "message": "неверный токен"
                                }
                        else:
                            return {
                                "status": "error",
                                "to_address": to_address,
                                "message": "неверный адрес отправки"
                            }
                    else:
                        return {"status": "error", "message": "не удалось получить данные"}
                else:
                    return {"status": "error", "message": f'не удалось подключиться к сайту ({response.status})'}
    except Exception as ex:
        traceback.print_exc()
        return {"status": "error", "message": str(ex)}
    else:
        return {"status": "error", "message": 'undefined'}


async def pyro_create_invoice(amount):
    try:
        await asyncio.sleep(1)
        results = await pyro_client_second.get_inline_bot_results('send', f'{str(amount)} USDT')
        # print(f"\nДанные: {results}")
        if results and results.results:
            for result in results.results:
                if result:
                    title = result.title or None
                    if title and str(title).startswith('Создать счёт'):
                        result_id = result.id or None
                        if result_id and str(result_id).startswith('invoice-'):
                            invoice_hash = result_id.split('invoice-')[1]
                            if invoice_hash:
                                response = await pyro_client_second.send_inline_bot_result(chat_id='me', query_id=results.query_id, result_id=result_id)
                                if response:
                                    return invoice_hash
    except Exception as e:
        traceback.print_exc()
    return None

async def create_cryptobot_invoice(user_id, amount, invoice_type=0):
    try:
        invoice_hash = await pyro_create_invoice(amount=amount)
        print(invoice_hash)
        if invoice_hash:
            sql = await add_cryptobot_payment(
                user_id=user_id,
                transaction_hash=invoice_hash,
                amount_usdt=float(amount),
                invoice_type=invoice_type,
            )
            return f'https://t.me/CryptoBot?start={invoice_hash}', 'undefined', sql.id
    except Exception as ex:
        traceback.print_exc()
        return None, '', None


async def pay_main_bill_link(invoice_hash):
    try:
        await asyncio.sleep(1)
        message_text = None
        account_balance = None
        callback_data = None
        invoice_hash = str(invoice_hash).replace('https://t.me/cryptobot?start=', '').replace('t.me/cryptobot?start=', '').replace('cryptobot?start=', '').replace('https://t.me/send?start=', '').replace('t.me/send?start=', '').replace('send?start=', '')
        if not invoice_hash:
            return None

        await asyncio.sleep(2)
        if not await pyro_client_second.send_message(chat_id='send', text=f'/start {invoice_hash}'):
            return None

        await asyncio.sleep(2)
        async for message in pyro_client_second.get_chat_history('send', limit=10):
            # print(message)
            if message and message.from_user.is_bot:
                try:
                    message_text = message.text
                except:
                    message_text = None
                if 'Пришлите сумму USDT для оплаты счёта.' in message_text and 'Ваш баланс: ' in message_text:
                    message_text = message_text.split('Ваш баланс: ')[1]
                    account_balance = message_text.split(' USDT')[0]
                    if account_balance:
                        break

        try:
            if account_balance:
                account_balance = float(account_balance)
        except:
            account_balance = None
        print(account_balance)
        if not account_balance:
            return None
        if account_balance >= 0.1:
            await asyncio.sleep(2)
            if not await pyro_client_second.send_message(chat_id='send', text=account_balance):
                return None

            await asyncio.sleep(2)
            async for message in pyro_client_second.get_chat_history('send', limit=10):
                # print(message)
                if message and message.from_user.is_bot:
                    try:
                        message_text = message.text
                    except:
                        message_text = None
                    if 'Подтвердите оплату счёта' in message_text and 'Вы уверены, что хотите оплатить этот счёт?' in message_text:
                        try:
                            for row in message.reply_markup.inline_keyboard:
                                for button in row:
                                    if button:
                                        if 'оплатить' in str(button.text).lower() and 'usdt' in str(button.text).lower():
                                            callback_data = button.callback_data
                        except:
                            traceback.print_exc()
                        if callback_data:
                            try:
                                await pyro_client_second.request_callback_answer(chat_id=message.chat.id, message_id=message.id, callback_data=callback_data)
                            except:
                                traceback.print_exc()
                            break

            await asyncio.sleep(2)
            async for message in pyro_client_second.get_chat_history('send', limit=10):
                # print(message)
                if message and message.from_user.is_bot:
                    try:
                        message_text = message.text
                    except:
                        message_text = None
                    if 'Вы уверены, что доверяете этому получателю?' in message_text:
                        if callback_data:
                            try:
                                await pyro_client_second.request_callback_answer(chat_id=message.chat.id, message_id=message.id, callback_data=message.reply_markup.inline_keyboard[0][0].callback_data)
                            except:
                                traceback.print_exc()
                            await asyncio.sleep(2)
    except:
        traceback.print_exc()






def famount(self):
    # return f"{self:.2f}".rstrip('0').rstrip('.')
    return f"{self:.6f}".rstrip('0').rstrip('.')



async def generate_random_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not await select_user(user_hash=code):
            return code




async def kick_user(bot, user_id):
    bt = await select_bot_setting()
    member = await BotGetChatMember(bot, chat_id=bt.op_group_id, user_id=user_id)
    if member and hasattr(member, 'status') and member.status == 'member':
        print(f'kick_user func: {user_id}')
        await BotBanChatMember(bot, chat_id=bt.op_group_id, user_id=user_id, revoke_messages=False)
        await BotUnBanChatMember(bot, chat_id=bt.op_group_id, user_id=user_id)



async def days_since(date_str, date_format="%Y-%m-%d"):
    try:
        given_date = datetime.strptime(str(date_str), date_format)
        today = datetime.today()
        delta = today - given_date
        return delta.days
    except:
        traceback.print_exc()
        return 0
async def days_since(date_str, date_format="%Y-%m-%d"):
    try:
        if isinstance(date_str, datetime):
            given_date = date_str
        else:
            try:
                given_date = datetime.strptime(str(date_str), date_format)
            except ValueError:
                try:
                    given_date = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
                        try:
                            given_date = datetime.strptime(str(date_str), fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError(f"Could not parse date: {date_str}")
        today = datetime.today()
        delta = today - given_date
        return delta.days
    except Exception as e:
        print(f"Error in days_since: {e}")
        traceback.print_exc()
        return 0
    
# async def days_since(date_str, date_format="%Y-%m-%d"):
#     try:
#         given_date = datetime.strptime(str(date_str), date_format)
#         today = datetime.today()
#         delta = today - given_date
#         return delta.days
#     except:
#         traceback.print_exc()
#         return 0


async def decline_times(n):
    if 11 <= n % 100 <= 14:
        form = "раз"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "раз"
        elif 2 <= remainder <= 4:
            form = "раза"
        else:
            form = "раз"
    return form


async def decline_day(n):
    if 11 <= n % 100 <= 14:
        form = "дней"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "день"
        elif 2 <= remainder <= 4:
            form = "дня"
        else:
            form = "дней"
    return form

async def decline_day_eng(n):
    if 11 <= n % 100 <= 14:
        form = "days"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "day"
        elif 2 <= remainder <= 4:
            form = "days"
        else:
            form = "days"
    return form

async def decline_number(n):
    if 11 <= n % 100 <= 14:
        form = "номеров"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "номер"
        elif 2 <= remainder <= 4:
            form = "номера"
        else:
            form = "номеров"
    return f"{form}"


async def decline_record(n):
    if 11 <= n % 100 <= 14:
        form = "записей"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "запись"
        elif 2 <= remainder <= 4:
            form = "записи"
        else:
            form = "записей"
    return f"{form}"


class ProxySaleAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://proxy-sale.com/personal/api/v1"

    async def get_russian_proxies(self) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{self.api_key}/resident/lists"
            async with session.get(url, headers={"Content-Type": "application/json"}) as response:
                result = await response.json()
                
                if result.get('status') != 'success':
                    raise Exception("Failed to get proxy list")
                
                russian_proxies = [
                    proxy for proxy in result['data']
                    if any(geo['country'] == 'RU' for geo in proxy['geo'])
                ]
                russian_proxies.sort(key=lambda x: x['id'], reverse=True)
                return russian_proxies

    async def download_proxy_details(self, proxy_id: int, proto: str) -> str:
        url = f"{self.base_url}/{self.api_key}/proxy/download/resident"
        params = {
            'listId': proxy_id,
            'ext': 'csv',
            'proto': proto # SOCKS5, HTTP > HTTPS
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers={'Accept': '*/*'}) as response:
                return await response.text()





# async def extract_tdata(archive_path, output_path, limit=None):
#     ext = archive_path.lower().split('.')[-1]
#     if ext == 'zip':
#         await asyncio.to_thread(_extract_zip, archive_path, output_path, limit=None)
#     elif ext == 'rar':
#         await asyncio.to_thread(_extract_rar, archive_path, output_path, limit=None)
#     elif ext == '7z':
#         await asyncio.to_thread(_extract_7z, archive_path, output_path, limit=None)
#     else:
#         print(f"Неподдерживаемый формат архива. ({archive_path} --- {output_path})")
#     await asyncio.to_thread(os.remove, archive_path)

# def _extract_zip(archive_path, output_path):
#     with zipfile.ZipFile(archive_path) as zf:
#         tdata_map = _collect_tdata_map(zf.infolist(), zip_mode=True)
#         _extract_from_map(zf, tdata_map, output_path, zip_mode=True)

# def _extract_rar(archive_path, output_path):
#     with rarfile.RarFile(archive_path) as rf:
#         tdata_map = _collect_tdata_map(rf.infolist())
#         _extract_from_map(rf, tdata_map, output_path)

# def _extract_7z(archive_path, output_path):
#     with py7zr.SevenZipFile(archive_path, mode='r') as sz:
#         members = sz.list()
#         tdata_map = _collect_tdata_map_7z(members)
#         _extract_from_map_7z(sz, tdata_map, output_path)

# def _collect_tdata_map(infolist, zip_mode=False):
#     tdata_map = defaultdict(list)
#     for info in infolist:
#         parts = pathlib.PurePath(info.filename).parts
#         idx = None
#         for i, p in enumerate(parts):
#             if p.lower().startswith('tdata'):
#                 idx = i
#                 break
#         if idx is not None:
#             tdata_folder_key = parts[:idx+1]
#             tdata_map[tdata_folder_key].append(info)
#     final_map = {}
#     count = 1
#     for folder_key, items in tdata_map.items():
#         has_file = any(not (item.is_dir() if zip_mode else item.isdir()) for item in items)
#         if has_file:
#             final_map[str(count)] = items
#             count += 1
#     return final_map

# def _collect_tdata_map_7z(members):
#     tdata_map = defaultdict(list)
#     for m in members:
#         parts = pathlib.PurePath(m.filename).parts
#         idx = None
#         for i, p in enumerate(parts):
#             if p.lower().startswith('tdata'):
#                 idx = i
#                 break
#         if idx is not None:
#             tdata_folder_key = parts[:idx+1]
#             tdata_map[tdata_folder_key].append(m)

#     final_map = {}
#     count = 1
#     for folder_key, items in tdata_map.items():
#         has_file = any(not it.is_directory for it in items)
#         if has_file:
#             final_map[str(count)] = items
#             count += 1
#     return final_map

# def _extract_from_map(archive_obj, tdata_map, output_path, zip_mode=False):
#     for folder_num, items in tdata_map.items():
#         out_folder = os.path.join(output_path, folder_num)
#         for info in items:
#             parts = pathlib.PurePath(info.filename).parts
#             idx = None
#             for i, p in enumerate(parts):
#                 if p.lower().startswith('tdata'):
#                     idx = i
#                     break
#             relative = parts[idx+1:] if idx is not None else ()
#             target_path = os.path.join(out_folder, *relative)
#             if zip_mode:
#                 if info.is_dir():
#                     os.makedirs(target_path, exist_ok=True)
#                 else:
#                     os.makedirs(os.path.dirname(target_path), exist_ok=True)
#                     with archive_obj.open(info) as src, open(target_path, 'wb') as dst:
#                         shutil.copyfileobj(src, dst)
#             else:
#                 if info.isdir():
#                     os.makedirs(target_path, exist_ok=True)
#                 else:
#                     os.makedirs(os.path.dirname(target_path), exist_ok=True)
#                     with archive_obj.open(info) as src, open(target_path, 'wb') as dst:
#                         shutil.copyfileobj(src, dst)

# def _extract_from_map_7z(sz_file, tdata_map, output_path):
#     for folder_num, items in tdata_map.items():
#         out_folder = os.path.join(output_path, folder_num)
#         names_to_extract = [m.filename for m in items if not m.is_directory]
#         if not names_to_extract:
#             continue
#         extracted_data = sz_file.read(names_to_extract)
#         for m in items:
#             parts = pathlib.PurePath(m.filename).parts
#             idx = None
#             for i, p in enumerate(parts):
#                 if p.lower().startswith('tdata'):
#                     idx = i
#                     break
#             relative = parts[idx+1:] if idx is not None else ()
#             target_path = os.path.join(out_folder, *relative)
#             if m.is_directory:
#                 os.makedirs(target_path, exist_ok=True)
#             else:
#                 os.makedirs(os.path.dirname(target_path), exist_ok=True)
#                 with open(target_path, 'wb') as dst:
#                     dst.write(extracted_data[m.filename].read())

















async def extract_session_files(archive_path, output_path, limit=None):
    os.makedirs(output_path, exist_ok=True)
    ext = os.path.splitext(archive_path.lower())[1]
    if ext == '.zip':
        await asyncio.to_thread(_s_extract_zip_sessions, archive_path, output_path, limit)
    elif ext == '.rar':
        await asyncio.to_thread(_s_extract_rar_sessions, archive_path, output_path, limit)
    elif ext in ['.7z', '.7zip']:
        await asyncio.to_thread(_s_extract_7z_sessions, archive_path, output_path, limit)
    else:
        print(f"Неподдерживаемый формат архива: {archive_path}")
    await asyncio.to_thread(os.remove, archive_path)
    session_count = len([f for f in os.listdir(output_path) if f.endswith('.session')])
    # if session_count == 0:
    #     print(f"Сессии не найдены в архиве {archive_path}")
    # else:
    #     print(f"Успешно извлечено {session_count} сессий из {archive_path}")

def _s_extract_zip_sessions(archive_path, output_path, limit=None):
    try:
        with zipfile.ZipFile(archive_path) as zf:
            session_files = _s_get_session_files_from_zip(zf)
            if not session_files:
                # print(f"В ZIP архиве {archive_path} не найдено файлов с расширением .session")
                return
            _s_extract_session_files_from_zip(zf, session_files, output_path, limit)
    except zipfile.BadZipFile:
        print(f"Ошибка: {archive_path} не является корректным ZIP архивом")
    except Exception as e:
        print(f"Ошибка при распаковке ZIP архива {archive_path}: {str(e)}")

def _s_extract_rar_sessions(archive_path, output_path, limit=None):
    try:
        with rarfile.RarFile(archive_path) as rf:
            session_files = _s_get_session_files_from_rar(rf)
            if not session_files:
                # print(f"В RAR архиве {archive_path} не найдено файлов с расширением .session")
                return
            _s_extract_session_files_from_rar(rf, session_files, output_path, limit)
    except rarfile.BadRarFile:
        print(f"Ошибка: {archive_path} не является корректным RAR архивом")
    except rarfile.RarCannotExec:
        print("Ошибка: Невозможно выполнить команду unrar. Убедитесь, что unrar установлен")
    except Exception as e:
        print(f"Ошибка при распаковке RAR архива {archive_path}: {str(e)}")

def _s_extract_7z_sessions(archive_path, output_path, limit=None):
    try:
        with py7zr.SevenZipFile(archive_path, mode='r') as sz:
            session_files = _s_get_session_files_from_7z(sz)
            if not session_files:
                # print(f"В 7Z архиве {archive_path} не найдено файлов с расширением .session")
                return
            _s_extract_session_files_from_7z(sz, session_files, output_path, limit)
    except py7zr.exceptions.Bad7zFile:
        print(f"Ошибка: {archive_path} не является корректным 7Z архивом")
    except Exception as e:
        print(f"Ошибка при распаковке 7Z архива {archive_path}: {str(e)}")

def _s_get_session_files_from_zip(zip_file):
    result = []
    for info in zip_file.infolist():
        if not info.is_dir() and info.filename.lower().endswith('.session'):
            result.append(info)
    return result

def _s_get_session_files_from_rar(rar_file):
    result = []
    for info in rar_file.infolist():
        if not info.isdir() and info.filename.lower().endswith('.session'):
            result.append(info)
    return result

def _s_get_session_files_from_7z(seven_zip_file):
    result = []
    file_list = seven_zip_file.list()
    for file_info in file_list:
        if not file_info.is_directory and file_info.filename.lower().endswith('.session'):
            result.append(file_info)
    return result

def _s_extract_session_files_from_zip(zip_file, session_files, output_path, limit=None):
    extracted_count = 0
    for i, info in enumerate(session_files, 1):
        if limit is not None and extracted_count >= limit:
            print(f"Достигнут лимит распаковки: {limit} файлов")
            break
        basename = os.path.basename(info.filename)
        target_path = os.path.join(output_path, f"{i}_{basename}")
        try:
            with zip_file.open(info) as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            extracted_count += 1
            # print(f"Извлечен файл: {basename} -> {target_path}")
        except Exception as e:
            print(f"Ошибка при извлечении {info.filename}: {str(e)}")

def _s_extract_session_files_from_rar(rar_file, session_files, output_path, limit=None):
    extracted_count = 0
    for i, info in enumerate(session_files, 1):
        if limit is not None and extracted_count >= limit:
            print(f"Достигнут лимит распаковки: {limit} файлов")
            break
        basename = os.path.basename(info.filename)
        target_path = os.path.join(output_path, f"{i}_{basename}")
        try:
            with rar_file.open(info) as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            extracted_count += 1
            # print(f"Извлечен файл: {basename} -> {target_path}")
        except Exception as e:
            print(f"Ошибка при извлечении {info.filename}: {str(e)}")

def _s_extract_session_files_from_7z(seven_zip_file, session_files, output_path, limit=None):
    extracted_count = 0
    if not session_files:
        return
    filenames_to_extract = [info.filename for info in session_files]
    try:
        extracted_data = seven_zip_file.read(filenames_to_extract)
        for i, info in enumerate(session_files, 1):
            if limit is not None and extracted_count >= limit:
                print(f"Достигнут лимит распаковки: {limit} файлов")
                break
            filename = info.filename
            if filename not in extracted_data:
                print(f"Файл {filename} не найден в извлеченных данных")
                continue
            basename = os.path.basename(filename)
            target_path = os.path.join(output_path, f"{i}_{basename}")
            try:
                with open(target_path, 'wb') as dst:
                    dst.write(extracted_data[filename].read())
                extracted_count += 1
                # print(f"Извлечен файл: {basename} -> {target_path}")
            except Exception as e:
                print(f"Ошибка при сохранении {filename}: {str(e)}")
    except Exception as e:
        print(f"Ошибка при извлечении файлов из 7Z архива: {str(e)}")

def _s_get_main_sessions_sync(root_directory: str) -> list[str]:
    return [str(item) for item in Path(root_directory).rglob('*.session') if item.is_file()]

async def get_main_sessions(root_directory: str) -> list[str]:
    return await asyncio.to_thread(_s_get_main_sessions_sync, root_directory)

async def convert_telethon_session_to_tdata(session_path: Path, tdata_folder_name: Path):
    if session_path and tdata_folder_name:
        try:
            session = await SessionManager.from_telethon_file(session_path, API.TelegramDesktop)
            await session.to_tdata_folder(tdata_folder_name)
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    return False







async def extract_tdata(archive_path, output_path, limit=None):
    ext = archive_path.lower().split('.')[-1]
    if ext == 'zip':
        await asyncio.to_thread(_extract_zip, archive_path, output_path, limit)
    elif ext == 'rar':
        await asyncio.to_thread(_extract_rar, archive_path, output_path, limit)
    elif ext == '7z':
        await asyncio.to_thread(_extract_7z, archive_path, output_path, limit)
    else:
        print(f"Неподдерживаемый формат архива. ({archive_path} --- {output_path})")
    await asyncio.to_thread(os.remove, archive_path)

def _extract_zip(archive_path, output_path, limit=None):
    with zipfile.ZipFile(archive_path) as zf:
        tdata_map = _collect_tdata_map(zf.infolist(), zip_mode=True)
        _extract_from_map(zf, tdata_map, output_path, zip_mode=True, limit=limit)

def _extract_rar(archive_path, output_path, limit=None):
    with rarfile.RarFile(archive_path) as rf:
        tdata_map = _collect_tdata_map(rf.infolist())
        _extract_from_map(rf, tdata_map, output_path, limit=limit)

def _extract_7z(archive_path, output_path, limit=None):
    with py7zr.SevenZipFile(archive_path, mode='r') as sz:
        members = sz.list()
        tdata_map = _collect_tdata_map_7z(members)
        _extract_from_map_7z(sz, tdata_map, output_path, limit=limit)

def _collect_tdata_map(infolist, zip_mode=False):
    tdata_map = defaultdict(list)
    for info in infolist:
        parts = pathlib.PurePath(info.filename).parts
        idx = None
        for i, p in enumerate(parts):
            if p.lower().startswith('tdata'):
                idx = i
                break
        if idx is not None:
            tdata_folder_key = parts[:idx+1]
            tdata_map[tdata_folder_key].append(info)
    final_map = {}
    count = 1
    for folder_key, items in tdata_map.items():
        has_file = any(not (item.is_dir() if zip_mode else item.isdir()) for item in items)
        if has_file:
            final_map[str(count)] = items
            count += 1
    return final_map

def _collect_tdata_map_7z(members):
    tdata_map = defaultdict(list)
    for m in members:
        parts = pathlib.PurePath(m.filename).parts
        idx = None
        for i, p in enumerate(parts):
            if p.lower().startswith('tdata'):
                idx = i
                break
        if idx is not None:
            tdata_folder_key = parts[:idx+1]
            tdata_map[tdata_folder_key].append(m)
    final_map = {}
    count = 1
    for folder_key, items in tdata_map.items():
        has_file = any(not it.is_directory for it in items)
        if has_file:
            final_map[str(count)] = items
            count += 1
    return final_map

def _extract_from_map(archive_obj, tdata_map, output_path, zip_mode=False, limit=None):
    file_count = 0
    for folder_num, items in tdata_map.items():
        out_folder = os.path.join(output_path, folder_num)
        for info in items:
            if limit is not None and file_count >= limit:
                print(f"Достигнут лимит распаковки: {limit} файлов")
                return
            parts = pathlib.PurePath(info.filename).parts
            idx = None
            for i, p in enumerate(parts):
                if p.lower().startswith('tdata'):
                    idx = i
                    break
            relative = parts[idx+1:] if idx is not None else ()
            target_path = os.path.join(out_folder, *relative)
            is_dir = info.is_dir() if zip_mode else info.isdir()
            if is_dir:
                os.makedirs(target_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with archive_obj.open(info) as src, open(target_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                file_count += 1

def _extract_from_map_7z(sz_file, tdata_map, output_path, limit=None):
    file_count = 0
    for folder_num, items in tdata_map.items():
        out_folder = os.path.join(output_path, folder_num)
        names_to_extract = [m.filename for m in items if not m.is_directory]
        if not names_to_extract:
            continue
        if limit is not None:
            remaining = limit - file_count
            if remaining <= 0:
                print(f"Достигнут лимит распаковки: {limit} файлов")
                return
            elif remaining < len(names_to_extract):
                names_to_extract = names_to_extract[:remaining]
        extracted_data = sz_file.read(names_to_extract)
        for m in items:
            if not m.is_directory:
                if m.filename not in extracted_data:
                    continue
                if limit is not None and file_count >= limit:
                    print(f"Достигнут лимит распаковки: {limit} файлов")
                    return
                parts = pathlib.PurePath(m.filename).parts
                idx = None
                for i, p in enumerate(parts):
                    if p.lower().startswith('tdata'):
                        idx = i
                        break
                relative = parts[idx+1:] if idx is not None else ()
                target_path = os.path.join(out_folder, *relative)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'wb') as dst:
                    dst.write(extracted_data[m.filename].read())
                file_count += 1
            else:
                parts = pathlib.PurePath(m.filename).parts
                idx = None
                for i, p in enumerate(parts):
                    if p.lower().startswith('tdata'):
                        idx = i
                        break
                relative = parts[idx+1:] if idx is not None else ()
                target_path = os.path.join(out_folder, *relative)
                os.makedirs(target_path, exist_ok=True)

def get_main_folders_sync(root_directory: str) -> list[str]:
    return [str(item) for item in Path(root_directory).iterdir() if item.is_dir()]

async def get_main_folders(root_directory: str) -> list[str]:
    return await asyncio.to_thread(get_main_folders_sync, root_directory)

async def convert_tdata_to_telethon_session(tdata: Path, session_path: str):
    try:
        if not tdata.exists():
            tdata.mkdir(parents=True)
        # print(f'API.TelegramDesktop: {API.TelegramDesktop}')
        session = SessionManager.from_tdata_folder(tdata)
        print(f'session: {session}')
        await session.to_telethon_file(session_path)
        print(f'session_path: {session_path}')
        return session_path
    except Exception as e:
        print(f"Ошибка: {e}")
        return False







async def convert_session_tdata(desktop: Path, tele: Path = None, password = None):
    if not desktop.exists():
        desktop.mkdir(parents=True)
    for item in desktop.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    if tele:
        try:
            session = await SessionManager.from_telethon_file(tele, API.TelegramDesktop)
            await session.to_tdata_folder(desktop)
            session_name = tele.stem
            archive_name = f"temp/{session_name}.zip"
            with zipfile.ZipFile(archive_name, 'w') as archive:
                for root, dirs, files in os.walk(desktop):
                    for file in files:
                        file_path = Path(root) / file
                        archive.write(file_path, arcname=file_path.relative_to(desktop))
                if password:
                    pass_file = desktop / f"pass_{password}"
                    pass_file.touch()
                    archive.write(pass_file, arcname=pass_file.name)
                    pass_file.unlink()
            return archive_name
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    return False


async def save_convert_session_tdata(path_folder: str, tele: Path = None, password = None, pack_id = None):
    if tele:
        try:
            if pack_id:
                session_folder = Path(path_folder) / f'{tele.stem}_{pack_id}'
            else:
                session_folder = Path(path_folder) / tele.stem
            session_folder.mkdir(parents=True, exist_ok=True)
            session = await SessionManager.from_telethon_file(tele, API.TelegramDesktop)
            await session.to_tdata_folder(session_folder)
            if password:
                pass_file = session_folder / f"pass_{password}"
                pass_file.touch()
            return str(session_folder)
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    return False


async def add_folder_to_archive(archive: zipfile.ZipFile, folder: Path):
    folder = Path(folder)
    if folder.is_dir():
        files_to_add = []
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(folder.parent)
                files_to_add.append((file_path, arcname))
        for file_path, arcname in files_to_add:
            await asyncio.to_thread(archive.write, file_path, arcname=arcname)

async def create_archive_from_folders(all_sessions: list[str | Path], archive_path: str | Path):
    all_sessions = [Path(folder) for folder in all_sessions]
    archive_path = Path(archive_path)
    print(f'all_sessions: {all_sessions}', f'archive_path: {archive_path}')
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in all_sessions:
            await add_folder_to_archive(archive, folder)
    return archive_path




async def add_file_to_archive(archive: zipfile.ZipFile, file: Path):
    file = Path(file)
    if file.is_file():
        arcname = file.name
        await asyncio.to_thread(archive.write, file, arcname=arcname)

async def create_archive_from_files(all_files: list[str | Path], archive_path: str | Path):
    all_files = [Path(file) for file in all_files]
    archive_path = Path(archive_path)
    print(f'all_files: {all_files}', f'archive_path: {archive_path}')
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in all_files:
            await add_file_to_archive(archive, file)
    return archive_path



async def add_folder_to_archive2(archive: zipfile.ZipFile, folder_path: Path, base_dir: Path = None):
    folder_path = Path(folder_path)
    if base_dir is None:
        base_dir = folder_path.parent
    for item in folder_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(base_dir)
            await asyncio.to_thread(archive.write, item, arcname=str(rel_path))

async def create_archive_from_folders2(all_folders: list[str | Path], archive_path: str | Path):
    all_folders = [Path(folder) for folder in all_folders]
    archive_path = Path(archive_path)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    # print(f'Создание архива: {archive_path}')
    # print(f'Добавление {len(all_folders)} папок')
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in all_folders:
            # print(f'Добавление папки: {folder}')
            common_base = folder.parent
            await add_folder_to_archive2(archive, folder, common_base)
    # print(f'Архив успешно создан: {archive_path}')
    return archive_path








# async def convert_session_tdata_2(desktop: Path, tele: Path = None):
#     if not desktop.exists():
#         desktop.mkdir(parents=True)
#     for item in desktop.iterdir():
#         if item.is_file():
#             item.unlink()
#         elif item.is_dir():
#             shutil.rmtree(item)
#     if tele:
#         try:
#             session = await SessionManager.from_telethon_file(tele, API.TelegramDesktop)
#             await session.to_tdata_folder(desktop)
#             session_name = tele.stem
#             archive_name = f"temp/tdata_{session_name}.zip"
#             with zipfile.ZipFile(archive_name, 'w') as archive:
#                 for root, dirs, files in os.walk(desktop):
#                     for file in files:
#                         file_path = Path(root) / file
#                         archive.write(file_path, arcname=file_path.relative_to(desktop))
#             return archive_name
#         except Exception as e:
#             print(f"Ошибка: {e}")
#             return False
#     return False





async def check_proxy(proxy):
    # print(proxy)
    try:
        connector = ProxyConnector.from_url(
            f"{proxy['scheme']}://{proxy['username']}:{proxy['password']}@{proxy['hostname']}:{proxy['port']}"
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get("https://api.ip.sb/ip", timeout=10) as response:
                if response.status in (200, 204, 401, 403):
                    return True
    except ProxyTimeoutError as e:
        print(f"Таймаут соединения с прокси: {proxy}", e)
    except ProxyError as e:
        if e.error_code == 407:
            print(f"Ошибка: Прокси требует аутентификации. {proxy}")
        else:
            print(f"Ошибка на стороне прокси: {proxy}", e)
    except (ClientConnectionError, asyncio.TimeoutError) as e:
        print(f"Проблема с соединением или тайм-аут: {proxy}", e)
    except asyncio.CancelledError:
        print(f"Запрос был отменен для прокси: {proxy}")
    except ClientSSLError as e:
        print(f"Ошибка SSL на стороне прокси: {proxy}", e)
    except ClientError as e:
        print(f"Общая ошибка клиента aiohttp: {proxy}", e)
    except ProxyConnectionError as e:
        print(f"Ошибка подключения к прокси: Не удалось подключиться к {proxy}", e)
    except ConnectionResetError as e:
        print(f"Соединение сброшено сервером или прокси: {proxy}", e)
    except Exception as e:
        if "Empty connect reply" in str(e):
            print(f"Пустой ответ от прокси: {proxy}")
        else:
            print(f"Неизвестная ошибка: {proxy}", e)
        traceback.print_exc()
    return False


async def get_total_profit(type=None, drop_id=None, client_id=None, group_id=None, otlega_unique_id=None, otlega_unique_id_is_none=None, otlega_count_days=None, client_bot=None, sletevshie=None, alive_status=None, alive_status_in=None, withdraw_status=None, only_withdraw_status=None, slet_last_at_is_none=None, slet_last_at_is_not_none=None):
    if sletevshie:
        slet_buyed_amount = 0
    total_amount = 0
    if type == '00_00':
        writes = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=17, buyed_at_00_00=True)
        if not sletevshie:
            if slet_last_at_is_not_none:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_last_at_00_00=True)
            else:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_at_00_00=True)
        deleted_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=21, payed_amount_total=True, deleted_at_00_00=True)
        if slet_last_at_is_not_none:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_last_at_00_00=True)
        else:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_at_00_00=True)
        unlocked_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, unban_month_status=1, unlocked_amount_total=True, unlocked_at_00_00=True)
        frozen_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=42, payed_amount_total=True, slet_at_00_00=True)
    elif type == 'yesterday':
        writes = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=17, buyed_at_yesterday=True)
        if not sletevshie:
            if slet_last_at_is_not_none:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_last_at_yesterday=True)
            else:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_at_yesterday=True)
        deleted_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=21, payed_amount_total=True, deleted_at_yesterday=True)
        if slet_last_at_is_not_none:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_last_at_yesterday=True)
        else:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_at_yesterday=True)
        unlocked_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, unban_month_status=1, unlocked_amount_total=True, unlocked_at_yesterday=True)
        frozen_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=42, payed_amount_total=True, slet_at_yesterday=True)
    elif type == 'week':
        writes = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=17, buyed_at_week=True)
        if not sletevshie:
            if slet_last_at_is_not_none:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_last_at_week=True)
            else:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_at_week=True)
        deleted_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=21, payed_amount_total=True, deleted_at_week=True)
        if slet_last_at_is_not_none:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_last_at_week=True)
        else:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_at_week=True)
        unlocked_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, unban_month_status=1, unlocked_amount_total=True, unlocked_at_week=True)
        frozen_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=42, payed_amount_total=True, slet_at_week=True)
    elif type == 'month':
        writes = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=17, buyed_at_month=True)
        if not sletevshie:
            if slet_last_at_is_not_none:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_last_at_month=True)
            else:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_at_month=True)
        deleted_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=21, payed_amount_total=True, deleted_at_month=True)
        if slet_last_at_is_not_none:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_last_at_month=True)
        else:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_at_month=True)
        unlocked_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, unban_month_status=1, unlocked_amount_total=True, unlocked_at_month=True)
        frozen_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=42, payed_amount_total=True, slet_at_month=True)
    elif type == 'previous_month':
        writes = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=17, buyed_at_previous_month=True)
        if not sletevshie:
            if slet_last_at_is_not_none:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_last_at_previous_month=True)
            else:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True, slet_at_previous_month=True)
        deleted_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=21, payed_amount_total=True, deleted_at_previous_month=True)
        if slet_last_at_is_not_none:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_last_at_previous_month=True)
        else:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True, slet_at_previous_month=True)
        unlocked_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, unban_month_status=1, unlocked_amount_total=True, unlocked_at_previous_month=True)
        frozen_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=42, payed_amount_total=True, slet_at_previous_month=True)
    else:
        writes = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=17)
        if not sletevshie:
            if slet_last_at_is_not_none:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True)
            else:
                slet_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=18, payed_amount_total=True)
        deleted_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=21, payed_amount_total=True)
        if slet_last_at_is_not_none:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True)
        else:
            not_valid_buyed_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=24, payed_amount_total=True)
        unlocked_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, unban_month_status=1, unlocked_amount_total=True)
        frozen_amount = await select_phone_queues(slet_last_at_is_not_none=slet_last_at_is_not_none, slet_last_at_is_none=slet_last_at_is_none, withdraw_status=withdraw_status, alive_status_in=alive_status_in, alive_status=alive_status, client_bot=client_bot, drop_id=drop_id, client_id=client_id, group_id=group_id, otlega_unique_id=otlega_unique_id, otlega_unique_id_is_none=otlega_unique_id_is_none, otlega_count_days=otlega_count_days, status=42, payed_amount_total=True)
    if writes:
        for write in writes:
            if write.buyed_amount and write.payed_amount:
                if write.referrer_amount:
                    if only_withdraw_status and write.withdraw_status == 0:
                        amount = write.buyed_amount
                        if write.referrer_amount:
                            amount -= write.referrer_amount
                        total_amount += amount
                    else:
                        if write.alive_hold_status == 1 and (not client_bot or (client_bot and write.client_bot == 0)):
                            amount = write.buyed_amount
                            if write.referrer_amount:
                                amount -= write.referrer_amount
                            total_amount += amount
                        else:
                            amount = write.buyed_amount - write.payed_amount
                            if write.referrer_amount:
                                amount -= write.referrer_amount
                            total_amount += amount
                else:
                    if only_withdraw_status and write.withdraw_status == 0:
                        total_amount += write.buyed_amount
                    else:
                        if write.alive_hold_status == 1 and (not client_bot or (client_bot and write.client_bot == 0)):
                            total_amount += write.buyed_amount
                        else:
                            amount = write.buyed_amount - write.payed_amount
                            total_amount += amount
    total_amount = total_amount - slet_buyed_amount - deleted_buyed_amount - not_valid_buyed_amount
    total_amount = total_amount + unlocked_amount
    total_amount = total_amount - frozen_amount
    return total_amount

def valid_phone(text):
    phone = str(text).replace('+', '').replace('(', '').replace(')', '').replace('-', '').replace('/', '').replace('\\', '').replace('.', '').replace(',', '').replace(' ', '')
    if phone:
        if phone[:1] == '8' and len(phone) == 11:
            phone = phone[1:]
        elif phone[:1] == '7' and len(phone) == 11:
            phone = phone[1:]
    if phone and len(phone) == 10 and phone.isdigit():
        return int(phone)
    return None


async def pyro_create_check(amount):
    try:
        await pyro_client.connect()
        await asyncio.sleep(15)
        results = await pyro_client.get_inline_bot_results('send', f'{str(amount)} USDT')
        await asyncio.sleep(5)
        # print(f"\nДанные: {results}")
        if results and results.results:
            for result in results.results:
                if result:
                    # print(f'result: {result}')
                    title = result.title or None
                    if title and str(title).startswith('Отправить'):
                        result_id = result.id or None
                        # print(result_id)
                        # print(result)
                        if result_id and str(result_id).startswith('check-'):
                            check_hash = result_id.split('check-')[1]
                            if check_hash:
                                response = await pyro_client.send_inline_bot_result(chat_id='me', query_id=results.query_id, result_id=result_id)
                                await asyncio.sleep(5)
                                # print(f'response: {response}')
                                if response:
                                    return check_hash
            return False
    except OSError as e:
        traceback.print_exc()
        return None
    except Exception as e:
        traceback.print_exc()
        return None
    finally:
        try:
            await pyro_client.disconnect()
        except:
            pass
    return None


async def pyro_cb_balance():
    try:
        await pyro_client.connect()
        await asyncio.sleep(1)
        await pyro_client.send_message('send', '/wallet')
        await asyncio.sleep(2)
        async for message in pyro_client.get_chat_history('send', limit=1):
            message_text = message.text
            
            available_match = re.search(r'Доступно:\s([\d\.]+)\sUSDT', message_text)
            if available_match:
                available_usdt = available_match.group(1)
                return available_usdt
            
            tether_match = re.search(r'Tether:\s([\d\.]+)\sUSDT', message_text)
            if tether_match:
                tether_usdt = tether_match.group(1)
                return tether_usdt
            return -1
    except OSError as e:
        traceback.print_exc()
        return -1
    except Exception as e:
        traceback.print_exc()
        return -1
    finally:
        try:
            await pyro_client.disconnect()
        except:
            pass
    return -1


async def decline_number(n):
    if 11 <= n % 100 <= 14:
        form = "номеров"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "номер"
        elif 2 <= remainder <= 4:
            form = "номера"
        else:
            form = "номеров"
    return f"{form}"


async def decline_record(n):
    if 11 <= n % 100 <= 14:
        form = "записей"
    else:
        remainder = n % 10
        if remainder == 1:
            form = "запись"
        elif 2 <= remainder <= 4:
            form = "записи"
        else:
            form = "записей"
    return f"{form}"


async def is_num_calc(s):
    pattern = r'^-?\d*(\.\d{1,2})?$'
    return re.match(pattern, s) is not None


async def decline_hours(number):
    last_digit = number % 10
    if 10 < number % 100 < 15:
        return f'Каждые {number} часов'
    if last_digit == 1:
        return f'Каждый {number} час'
    elif 1 < last_digit < 5:
        return f'Каждые {number} часа'
    else:
        return f'Каждые {number} часов'


async def decline_hours_2(number):
    last_digit = number % 10
    if 10 < number % 100 < 15:
        return f'{number} часов'
    if last_digit == 1:
        return f'{number} час'
    elif 1 < last_digit < 5:
        return f'{number} часа'
    else:
        return f'{number} часов'


async def decline_minutes(number):
    last_digit = number % 10
    if 10 < number % 100 < 15:
        return f'Каждые {number} минут'
    if last_digit == 1:
        return f'Каждую {number} минуту'
    elif 1 < last_digit < 5:
        return f'Каждые {number} минуты'
    else:
        return f'Каждые {number} минут'


async def find_mention_ids(text):
	try:
		pattern = r'id=(\d+)'
		ids = re.findall(pattern, text)
		int_ids = [int(id) for id in ids]
		return list(set(int_ids))
	except:
		return []


async def get_emoji_role(type):
	types = {
		'client': '🥷',
		'drop': '👨‍💻',
		'admin': '⭐️'
	}
	return types.get(type, '')


async def extract_write_id(text):
    match = re.search(r'tg://sql\?write_id=(\d+)', text)
    if match:
        return match.group(1)
    return None


async def declension(number, word_forms):
    if 11 <= number % 100 <= 19:
        return word_forms[2]
    if number % 10 == 1:
        return word_forms[0]
    if 2 <= number % 10 <= 4:
        return word_forms[1]
    return word_forms[2]

async def format_time(seconds):
    if seconds < 60:
        return f"{seconds} {await declension(seconds, ['сек.', 'сек.', 'сек.'])}"
    total_minutes = seconds // 60
    seconds = seconds % 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    result = []
    if hours > 0:
        result.append(f"{hours} {await declension(hours, ['час', 'часа', 'часов'])}")
    if minutes > 0:
        result.append(f"{minutes} {await declension(minutes, ['мин.', 'мин.', 'мин.'])}")
    if seconds > 0:
        result.append(f"{seconds} {await declension(seconds, ['сек.', 'сек.', 'сек.'])}")
    return ' '.join(result)


async def time_difference(start, end):
    delta = end - start
    total_seconds = int(delta.total_seconds())
    return await format_time(seconds=total_seconds) if total_seconds else 0

async def seconds_difference(start, end):
    delta = end - start
    return int(delta.total_seconds())

async def different_time(given_time_str, count_minutes):
    time_difference = datetime.now() - datetime.strptime(str(given_time_str), "%Y-%m-%d %H:%M:%S.%f")
    return time_difference >= timedelta(minutes=count_minutes)

async def different_time_seconds(given_time_str, count_seconds):
    time_difference = datetime.now() - datetime.strptime(str(given_time_str), "%Y-%m-%d %H:%M:%S.%f")
    return time_difference >= timedelta(seconds=count_seconds)


async def get_application_status(type):
	types = {
		0: 'на рассмотрении',
		1: 'одобрена',
		2: 'отклонена'
	}
	return types.get(type, '')


async def get_application_status_emoji(type):
	types = {
		0: '⏳',
		1: '✅',
		2: '❌'
	}
	return types.get(type, '')


async def get_minutes_ban(type):
	types = {
		0: 10,
		1: 30,
		2: 60,
		3: 180,
		4: 360
	}
	response = types.get(type, '')
	if not response:
		response = types.get(4, '')
	return response


async def user_declination(num):
    if 11 <= num % 100 <= 14:
        return 'пользователям'
    elif num % 10 == 1:
        return 'пользователю'
    else:
        return 'пользователям'

async def get_phone_queue_main_status(type=None, r_all=False):
	types = {
        0: 'в очереди на авторизации',
        1: 'авторизация',
        2: 'не удалось найти прокси',
        3: 'дроп не прислал верный смс',
        4: 'на аккаунте установлен пароль',
        5: 'истёк срок действия кода',
        6: 'авторизован, установка пароля',
        7: 'не удалось установить пароль',
        8: 'пароль установлен, ожидание сброса сессий',
        9: 'сессии не были сброшены',
        10: 'на аккаунте флудвейт',
        11: 'на аккаунте спамблок',
        12: 'добавлен',
        13: 'не удалось авторизоваться',
        14: 'клиент взял аккаунт на авторизацию',
        15: 'клиент запросил смс',
        16: 'не удалось получить смс',
        17: 'подтверждён',
        18: 'слёт',
        19: 'удалён дропом',
        20: 'удалён админом',
        21: 'удалён выплаченный',
        22: 'холд 24 часа (нет смс)',
        23: 'сессия слетела',
        24: 'слетела выплаченная сессия',
        25: 'дроп отменил авторизацию',
        26: 'номер заблокирован',
        27: 'не удалось отправить смс авторизации',
        28: 'неверный номер телефона',
        29: 'номер не зарегистрирован в тг',
        30: 'не удалось ввести код авторизации',
        31: 'не авторизован',
        32: 'не удалось получить валидный прокси',
        33: 'ручной забор тдаты',
        34: 'обработка тдаты',
        35: 'обработка аккаунта (клиентский бот)',
        36: 'запрос кода авторизации (клиентский бот)',
        37: 'не удалось отправить сообщение для проверки спамблока',
        38: 'теневой бан',
        39: 'не удалось проверить теневой бан',
        40: 'проверка на слёт',
        41: 'аккаунт заморожен',
        42: 'заморожен выплаченный аккаунт',
	}
	if r_all:
		return [[key, value] for key, value in types.items()]
	else:
		return types.get(type, '')

async def get_alive_status(type=None, r_all=False):
	types = {
        0: 'не проверен',
        1: 'невалид',
        2: 'теневой бан',
        3: 'спамблок',
        9: 'прошёл проверку',
        10: 'на проверке',
	}
	if r_all:
		return [[key, value] for key, value in types.items()]
	else:
		return types.get(type, '')


async def get_write_info(write):
    header = "<b>ℹ️ Информация о записи:</b>"
    field_lines = []
    field_lines.append(f"<b>Клиентский бот</b>: <code>{'✅ да' if write.client_bot == 1 else 'нет'}</code>")
    if getattr(write, 'id', None):
        field_lines.append(f"<b>ID</b>: <code>{write.id}</code>")
    if getattr(write, 'group_id', None):
        group_val = f"/gid{str(write.group_id).replace('-', '')}"
        field_lines.append(f"<b>Группа</b>: {group_val}")
    if getattr(write, 'client_id', None):
        field_lines.append(f"<b>Клиент</b>: /uid{write.client_id}")
    if getattr(write, 'drop_id', None):
        field_lines.append(f"<b>Дроп</b>: /uid{write.drop_id}")
    if getattr(write, 'referrer_id', None):
        field_lines.append(f"<b>Рефевод</b>: /uid{write.referrer_id}")
    if getattr(write, 'group_user_id', None):
        field_lines.append(f"<b>Покупатель в группе</b>: /uid{write.group_user_id}")
    if getattr(write, 'phone_number', None):
        field_lines.append(f"<b>Номер</b>: <code>{write.phone_number}</code>")
    if getattr(write, 'password', None):
        field_lines.append(f"<b>Пароль</b>: <code>{write.password}</code>")
    if getattr(write, 'last_auth_code', None):
        field_lines.append(f"<b>Последний код</b>: <code>{write.last_auth_code}</code>")
    if getattr(write, 'status', None) is not None:
        status_str = await get_phone_queue_main_status(write.status)
        field_lines.append(f"<b>Статус</b>: <code>{status_str}</code>")
    if getattr(write, 'status', None) is not None:
        status_str = await get_alive_status(write.alive_status)
        field_lines.append(f"<b>Статус проверки</b>: <code>{status_str}</code>")
    if getattr(write, 'buyed_at', None):
        field_lines.append(f"<b>Время покупки</b>: {write.buyed_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'slet_at', None):
        field_lines.append(f"<b>Время слёта</b>: {write.slet_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'set_at', None):
        field_lines.append(f"<b>Время добавления</b>: {write.set_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'readded_at', None):
        field_lines.append(f"<b>Время повторного добавления</b>: {write.readded_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'deleted_at', None):
        field_lines.append(f"<b>Время удаления</b>: {write.deleted_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'added_at', None):
        field_lines.append(f"<b>Время вбива</b>: {write.added_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'withdraw_at', None):
        field_lines.append(f"<b>Время вывода</b>: {write.withdraw_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'unlocked_at', None):
        field_lines.append(f"<b>Время выкупа</b>: {write.unlocked_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'updated_at', None):
        field_lines.append(f"<b>Последнее обновление</b>: {write.updated_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'last_check_at', None):
        field_lines.append(f"<b>Последняя проверка</b>: {write.last_check_at.strftime('%d.%m.%Y г. в %H:%M:%S')}")
    if getattr(write, 'withdraw_status', None) is not None:
        ws = "<code>✅ да</code>" if write.withdraw_status == 1 else "<code>нет</code>"
        field_lines.append(f"<b>Выплачено криптоботом</b>: {ws}")
    if getattr(write, 'skip_count', None) is not None:
        field_lines.append(f"<b>Количество пропусков</b>: <code>{write.skip_count}</code>")
    if getattr(write, 'skip_group_id_1', None):
        field_lines.append(f"<b>ID первой пропущенной группы</b>: <code>{write.skip_group_id_1}</code>")
    if getattr(write, 'skip_group_id_2', None):
        field_lines.append(f"<b>ID второй пропущенной группы</b>: <code>{write.skip_group_id_2}</code>")
    if getattr(write, 'withdraw_id', None):
        field_lines.append(f"<b>ID вывода</b>: <code>{write.withdraw_id}</code>")
    if getattr(write, 'payed_amount', None):
        field_lines.append(f"<b>Выплаченная сумма</b>: <code>{write.payed_amount:.2f}$</code>")
    if getattr(write, 'buyed_amount', None):
        field_lines.append(f"<b>Купленная сумма</b>: <code>{write.buyed_amount:.2f}$</code>")
    if getattr(write, 'unlocked_amount', None):
        field_lines.append(f"<b>Разблокированная сумма</b>: <code>{write.unlocked_amount:.2f}$</code>")
    if getattr(write, 'referrer_amount', None):
        field_lines.append(f"<b>Получено рефеводом</b>: <code>{write.referrer_amount:.2f}$</code>")
    if getattr(write, 'auth_proxy', None) and isinstance(write.auth_proxy, dict):
        if write.auth_proxy.get("scheme"):
            field_lines.append(f"<b>Тип прокси</b>: <code>{write.auth_proxy['scheme']}</code>")
        if all(k in write.auth_proxy for k in ("username", "password", "hostname", "port")):
            proxy_val = f"{write.auth_proxy['username']}:{write.auth_proxy['password']}@{write.auth_proxy['hostname']}:{int(write.auth_proxy['port'])}"
            field_lines.append(f"<b>Прокси</b>: <code>{proxy_val}</code>")
    if getattr(write, 'session_name', None):
        field_lines.append(f"<b>Сессия</b>: <code>{write.session_name}</code>")
    if getattr(write, 'otlega_unique_id', None):
        field_lines.append(f"<b>Отлега (DEV_ID)</b>: <code>{write.otlega_unique_id}</code>")
    if getattr(write, 'otlega_count_days', None):
        field_lines.append(f"<b>Отлега (кол-во дней)</b>: <code>{write.otlega_count_days}</code>")
    dynamic_lines = []
    for index, line in enumerate(field_lines):
        prefix = "└ " if index == len(field_lines) - 1 else "├ "
        dynamic_lines.append(f"{prefix}{line}")
    return "\n".join([header] + dynamic_lines)



# async def get_write_info(write):
#     return (
#         '<b>ℹ️ Информация о записи:</b>'
#         f'\n<b>├ Клиентский бот:</b> <code>{"✅ да" if write.client_bot == 1 else "нет"}</code>'
#         f'\n<b>├ ID:</b> <code>{write.id}</code>'
#         f'''\n<b>├ Группа:</b> {f"/gid{str(write.group_id).replace('-', '')}" if write.group_id else "<code>отсутствует</code>"}'''
#         f'\n<b>├ Клиент:</b> {f"/uid{write.client_id}" if write.client_id else "<code>отсутствует</code>"}'
#         f'\n<b>├ Дроп:</b> {f"/uid{write.drop_id}" if write.drop_id else "<code>отсутствует</code>"}'
#         f'\n<b>├ Рефевод:</b> {f"/uid{write.referrer_id}" if write.referrer_id else "<code>отсутствует</code>"}'
#         f'\n<b>├ Покупатель в группе:</b> {f"/uid{write.group_user_id}" if write.group_user_id else "<code>отсутствует</code>"}'
#         f'\n<b>├ Номер:</b> {f"<code>{write.phone_number}</code>" if write.phone_number else "<code>отсутствует</code>"}'
#         f'\n<b>├ Пароль:</b> <code>{write.password if write.password else "отсутствует"}</code>'
#         f'\n<b>├ Последний код:</b> {f"<code>{write.last_auth_code}</code>" if write.last_auth_code else "<code>отсутствует</code>"}'
#         f'\n<b>├ Статус:</b> {f"<code>{await get_phone_queue_main_status(write.status)}</code>" if write.status is not None else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время покупки:</b> {write.buyed_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.buyed_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время слёта:</b> {write.slet_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.slet_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время добавления:</b> {write.set_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.set_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время повторного добавления:</b> {write.readded_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.readded_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время удаления:</b> {write.deleted_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.deleted_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время вбива:</b> {write.added_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.added_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время вывода:</b> {write.withdraw_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.withdraw_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Время выкупа:</b> {write.unlocked_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.unlocked_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Последнее обновление:</b> {write.updated_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.updated_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Последняя проверка:</b> {write.last_check_at.strftime("%d.%m.%Y г. в %H:%M:%S") if write.last_check_at else "<code>отсутствует</code>"}'
#         f'\n<b>├ Выплачено криптоботом:</b> <code>{"✅ да" if write.withdraw_status == 1 else "нет"}</code>'
#         f'\n<b>├ Количество пропусков:</b> <code>{write.skip_count}</code>'
#         f'\n<b>├ ID первой пропущенной группы:</b> <code>{write.skip_group_id_1 if write.skip_group_id_1 else "отсутствует"}</code>'
#         f'\n<b>├ ID второй пропущенной группы:</b> <code>{write.skip_group_id_2 if write.skip_group_id_2 else "отсутствует"}</code>'
#         f'\n<b>├ ID вывода:</b> <code>{write.withdraw_id if write.withdraw_id else "отсутствует"}</code>'
#         f'\n<b>├ Выплаченная сумма:</b> <code>{f"{write.payed_amount:.2f}$" if write.payed_amount else "отсутствует"}</code>'
#         f'\n<b>├ Купленная сумма:</b> <code>{f"{write.buyed_amount:.2f}$" if write.buyed_amount else "отсутствует"}</code>'
#         f'\n<b>├ Разблокированная сумма:</b> <code>{f"{write.unlocked_amount:.2f}$" if write.unlocked_amount else "отсутствует"}</code>'
#         f'\n<b>├ Получено рефеводом:</b> <code>{f"{write.referrer_amount:.2f}$" if write.referrer_amount else "отсутствует"}</code>'
#         f'\n<b>├ Тип прокси:</b> <code>{write.auth_proxy["scheme"] if write.auth_proxy else "отсутствует"}</code>'
#         f'\n<b>├ Прокси:</b> <code>{f"""{write.auth_proxy["username"]}:{write.auth_proxy["password"]}@{write.auth_proxy["hostname"]}:{int(write.auth_proxy["port"])}""" if write.auth_proxy else """отсутствует"""}</code>'
#         f'\n<b>├ Сессия:</b> {f"<code>{write.session_name}</code>" if write.session_name else "<code>отсутствует</code>"}'
#         f'\n<b>├ Отлега (DEV_ID):</b> {f"<code>{write.otlega_unique_id}</code>" if write.otlega_unique_id else "<code>отсутствует</code>"}'
#         f'\n<b>└ Отлега (кол-во дней):</b> {f"<code>{write.otlega_count_days}</code>" if write.otlega_count_days else "<code>отсутствует</code>"}'
#     )


async def get_write_info_dynamic(write):
    def format_date(date):
        return date.strftime("%d.%m.%Y г. в %H:%M:%S") if date else "<code>отсутствует</code>"
    fields = {
        'Клиентский бот': f'<code>{"✅ да" if write.client_bot == 1 else "нет"}</code>',
        'ID': f'<code>{write.id}</code>',
        'Группа': f'/gid{str(write.group_id).replace("-", "")}' if write.group_id else "<code>отсутствует</code>",
        'Клиент': f'/uid{write.client_id}' if write.client_id else "<code>отсутствует</code>",
        'Дроп': f'/uid{write.drop_id}' if write.drop_id else "<code>отсутствует</code>",
        'Рефевод': f'/uid{write.referrer_id}' if write.referrer_id else "<code>отсутствует</code>",
        'Покупатель в группе': f'/uid{write.group_user_id}' if write.group_user_id else "<code>отсутствует</code>",
        'Номер': f'<code>{write.phone_number}</code>' if write.phone_number else "<code>отсутствует</code>",
        'Пароль': f'<code>{write.password}</code>' if write.password else "<code>отсутствует</code>",
        'Последний код': f'<code>{write.last_auth_code}</code>' if write.last_auth_code else "<code>отсутствует</code>",
        'Статус': f'<code>{await get_phone_queue_main_status(write.status)}</code>' if write.status is not None else "<code>отсутствует</code>",
        'Время покупки': format_date(write.buyed_at),
        'Время слёта': format_date(write.slet_at),
        'Время добавления': format_date(write.set_at),
        'Время повторного добавления': format_date(write.readded_at),
        'Время удаления': format_date(write.deleted_at),
        'Время вбива': format_date(write.added_at),
        'Время вывода': format_date(write.withdraw_at),
        'Последнее обновление': format_date(write.updated_at),
        'Последняя проверка': format_date(write.last_check_at),
        'Выплачено криптоботом': '<code>✅ да</code>' if write.withdraw_status == 1 else '<code>нет</code>',
        'Количество пропусков': f'<code>{write.skip_count}</code>',
        'ID первой пропущенной группы': f'<code>{write.skip_group_id_1}</code>' if write.skip_group_id_1 else "<code>отсутствует</code>",
        'ID второй пропущенной группы': f'<code>{write.skip_group_id_2}</code>' if write.skip_group_id_2 else "<code>отсутствует</code>",
        'ID вывода': f'<code>{write.withdraw_id}</code>' if write.withdraw_id else "<code>отсутствует</code>",
        'Выплаченная сумма': f'<code>{write.payed_amount:.2f}$</code>' if write.payed_amount else "<code>отсутствует</code>",
        'Купленная сумма': f'<code>{write.buyed_amount:.2f}$</code>' if write.buyed_amount else "<code>отсутствует</code>",
        'Получено рефеводом': f'<code>{write.referrer_amount:.2f}$</code>' if write.referrer_amount else "<code>отсутствует</code>",
        'Тип прокси': f'<code>{write.auth_proxy["scheme"]}</code>' if write.auth_proxy else "<code>отсутствует</code>",
        'Прокси': f'<code>{write.auth_proxy["username"]}:{write.auth_proxy["password"]}@{write.auth_proxy["hostname"]}:{int(write.auth_proxy["port"])}</code>' if write.auth_proxy else "<code>отсутствует</code>",
        'Сессия': f'<code>{write.session_name}</code>' if write.session_name else "<code>отсутствует</code>",
        'Отлега (DEV_ID)': f'<code>{write.otlega_unique_id}</code>' if write.otlega_unique_id else "<code>отсутствует</code>",
        'Отлега (кол-во дней)': f'<code>{write.otlega_count_days}</code>' if write.otlega_count_days else "<code>отсутствует</code>"
    }
    result = ['<b>ℹ️ Информация о записи:</b>']
    field_items = list(fields.items())
    for i, (key, value) in enumerate(field_items):
        prefix = '└' if i == len(field_items) - 1 else '├'
        if value not in [None, "<code>отсутствует</code>"]:
            result.append(f'<b>{prefix} {key}:</b> {value}')
    return '\n'.join(result)


async def get_nevalid_session_info(user_info, write):
    bt = await select_bot_setting()
    return (
        f'<b>☠️ Слетела сессия <code>{write.phone_number}</code></b>'
        f'\n<b>├ Заблокирован:</b> <code>{"✅ да" if user_info.is_banned else "❌ нет"}</code> {f"(🤖 авто)" if user_info.is_banned and user_info.auto_ban_status else ""}'
        f'\n<b>├ Автоблокировка:</b> <code>{f"была ({user_info.auto_ban_count} {await decline_times(user_info.auto_ban_count)})" if user_info.auto_ban_count else "отсутствует"}</code>'
        f'\n<b>├ ID:</b> <code>{user_info.user_id}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
        f'\n<b>├ Регистрация:</b> {user_info.registered_at.strftime("%d.%m.%Y г. в %H:%M")}'
        f'\n<b>├ Автовывод:</b> <code>{"✅ вкл." if user_info.auto_withdraw_status else "выкл."}</code>'
        f'\n<b>├ Стандартное значение:</b> {"" if user_info.calc_amount else "🤖 "}{(user_info.calc_amount if user_info.calc_amount else bt.main_drop_calc_amount):.2f}$'
        f'\n<b>├ Оплаченных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_month=True))})</code>'
        f'\n<b>├ Выданных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_month=True))})</code>'
        f'\n<b>├ Слетевших за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_month=True))})</code>'
        f'\n<b>├ Удалённых за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_month=True))})</code>'
        f'\n<b>├ Невалидных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_month=True))})</code>'
        f'\n<b>├ Замороженных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_month=True))})</code>'
        f'\n<b>├ Оплатил за месяц:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_month=True))})</code>'
        f'\n<b>├ Прибыль за месяц:</b> <code>{await get_total_profit("month", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>├ Убытки за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$</code>'
        f'\n<b>├ Оплаченных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_previous_month=True))})</code>'
        f'\n<b>├ Выданных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_previous_month=True))})</code>'
        f'\n<b>├ Слетевших за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Удалённых за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_previous_month=True))})</code>'
        f'\n<b>├ Невалидных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Замороженных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Оплатил за предыдущий месяц:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_previous_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_previous_month=True))})</code>'
        f'\n<b>├ Прибыль за предыдущий месяц:</b> <code>{await get_total_profit("previous_month", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>├ Убытки за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$</code>'
        f'\n<b>├ Прибыль за всё время:</b> <code>{await get_total_profit("", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>└ Убытки за всё время:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True):.2f}$</code>'
    
        f'\n\n<blockquote expandable>{await get_write_info_dynamic(write)}</blockquote>'
    )

async def get_frozen_session_info(user_info, write):
    bt = await select_bot_setting()
    return (
        f'<b>❄️ Заморожен аккаунт <code>{write.phone_number}</code></b>'
        f'\n<b>├ Заблокирован:</b> <code>{"✅ да" if user_info.is_banned else "❌ нет"}</code> {f"(🤖 авто)" if user_info.is_banned and user_info.auto_ban_status else ""}'
        f'\n<b>├ Автоблокировка:</b> <code>{f"была ({user_info.auto_ban_count} {await decline_times(user_info.auto_ban_count)})" if user_info.auto_ban_count else "отсутствует"}</code>'
        f'\n<b>├ ID:</b> <code>{user_info.user_id}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
        f'\n<b>├ Регистрация:</b> {user_info.registered_at.strftime("%d.%m.%Y г. в %H:%M")}'
        f'\n<b>├ Автовывод:</b> <code>{"✅ вкл." if user_info.auto_withdraw_status else "выкл."}</code>'
        f'\n<b>├ Стандартное значение:</b> {"" if user_info.calc_amount else "🤖 "}{(user_info.calc_amount if user_info.calc_amount else bt.main_drop_calc_amount):.2f}$'
        f'\n<b>├ Оплаченных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_month=True))})</code>'
        f'\n<b>├ Выданных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_month=True))})</code>'
        f'\n<b>├ Слетевших за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_month=True))})</code>'
        f'\n<b>├ Удалённых за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_month=True))})</code>'
        f'\n<b>├ Невалидных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_month=True))})</code>'
        f'\n<b>├ Замороженных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_month=True))})</code>'
        f'\n<b>├ Оплатил за месяц:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_month=True))})</code>'
        f'\n<b>├ Прибыль за месяц:</b> <code>{await get_total_profit("month", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>├ Убытки за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$</code>'
        f'\n<b>├ Оплаченных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_previous_month=True))})</code>'
        f'\n<b>├ Выданных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_previous_month=True))})</code>'
        f'\n<b>├ Слетевших за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Удалённых за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_previous_month=True))})</code>'
        f'\n<b>├ Невалидных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Замороженных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Оплатил за предыдущий месяц:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_previous_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_previous_month=True))})</code>'
        f'\n<b>├ Прибыль за предыдущий месяц:</b> <code>{await get_total_profit("previous_month", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>├ Убытки за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$</code>'
        f'\n<b>├ Прибыль за всё время:</b> <code>{await get_total_profit("", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>└ Убытки за всё время:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True):.2f}$</code>'
        f'\n\n<blockquote expandable>{await get_write_info_dynamic(write)}</blockquote>'
    )


async def get_user_bans_theme_info(user_info):
    bt = await select_bot_setting()
    return (
        f'\n<b>├ ID:</b> <code>{user_info.user_id}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
        f'\n<b>├ Регистрация:</b> {user_info.registered_at.strftime("%d.%m.%Y г. в %H:%M")}'
        f'\n<b>├ Автовывод:</b> <code>{"✅ вкл." if user_info.auto_withdraw_status else "выкл."}</code>'
        f'\n<b>├ Стандартное значение:</b> {"" if user_info.calc_amount else "🤖 "}{(user_info.calc_amount if user_info.calc_amount else bt.main_drop_calc_amount):.2f}$'
        f'\n<b>├ Оплаченных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_month=True))})</code>'
        f'\n<b>├ Выданных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_month=True))})</code>'
        f'\n<b>├ Слетевших за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_month=True))})</code>'
        f'\n<b>├ Удалённых за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_month=True))})</code>'
        f'\n<b>├ Невалидных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_month=True))})</code>'
        f'\n<b>├ Замороженных за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_month=True))})</code>'
        f'\n<b>├ Оплатил за месяц:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_month=True))})</code>'
        f'\n<b>├ Прибыль за месяц:</b> <code>{await get_total_profit("month", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>├ Убытки за месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$</code>'
        f'\n<b>├ Оплаченных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_previous_month=True))})</code>'
        f'\n<b>├ Выданных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_previous_month=True))})</code>'
        f'\n<b>├ Слетевших за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Удалённых за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_previous_month=True))})</code>'
        f'\n<b>├ Невалидных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Замороженных за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_previous_month=True))})</code>'
        f'\n<b>├ Оплатил за предыдущий месяц:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_previous_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_previous_month=True))})</code>'
        f'\n<b>├ Прибыль за предыдущий месяц:</b> <code>{await get_total_profit("previous_month", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>├ Убытки за предыдущий месяц:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$</code>'
        f'\n<b>├ Прибыль за всё время:</b> <code>{await get_total_profit("", drop_id=user_info.user_id):.2f}$</code>'
        f'\n<b>└ Убытки за всё время:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True):.2f}$</code>'
    )


async def get_write_info_for_client(write):
    return (
        '<b>ℹ️ Информация об аккаунте:</b>'
        f"{f'{chr(10)}<b>├ Купил:</b> <code>{write.group_user_id}</code>' if write.group_user_id else ''}"
        f'\n<b>├ Номер:</b> {f"<code>{write.phone_number}</code>" if write.phone_number else "<code>-</code>"}'
        f'\n<b>├ Пароль:</b> <code>{write.password if write.password else "-"}</code>'
        f'\n<b>├ Отлега:</b> {f"<code>{write.otlega_count_days} {await decline_day(int(write.otlega_count_days))}</code>" if write.otlega_count_days else "<code>-/code>"}'
        f'\n<b>├ Время добавления:</b> {write.set_at.strftime("%d.%m.%Y %H:%M") if write.set_at else "<code>-</code>"}'
        f'\n<b>└ Время покупки:</b> {write.buyed_at.strftime("%d.%m.%Y %H:%M") if write.buyed_at else "<code>-</code>"}'
    )


async def calculate_hold_time(set_at_str, count_days):
   set_at = datetime.fromisoformat(str(set_at_str))
   end_date = set_at + timedelta(days=count_days)
   now = datetime.now()
   remaining = end_date - now
   if remaining.total_seconds() <= 0:
       return "✅"
   days = remaining.days
   hours = remaining.seconds // 3600
   minutes = (remaining.seconds % 3600) // 60
   seconds = remaining.seconds % 60
   result = []
   if days > 0:
       result.append(f"{days} дн.")
   if hours > 0:
       result.append(f"{hours} ч.")
   if minutes > 0:
       result.append(f"{minutes} мин.")
   if seconds > 0 or not result:
       result.append(f"{seconds} сек.")
   return " ".join(result)


async def get_drop_qr_code_info(write):
	return (
		'<b>ℹ️ Информация о записи:</b>'
	)

async def get_user_info(user_info):
    bt = await select_bot_setting()
    if user_info.role == 'client':
        stat = (
            '\n\n<b>☀️ За сегодня:</b>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_00_00=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=17, buyed_at_00_00=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_00_00=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=18, slet_at_00_00=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_00_00=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=21, deleted_at_00_00=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_00_00=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=24, slet_at_00_00=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_00_00=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=42, slet_at_00_00=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("00_00", client_id=user_info.user_id):.2f}$</code>'
            f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_00_00=True) + await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_00_00=True) + await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_00_00=True) + await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_00_00=True):.2f}$</code>'

            '\n\n<b>🌑 За вчера:</b>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_yesterday=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=17, buyed_at_yesterday=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_yesterday=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=18, slet_at_yesterday=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_yesterday=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=21, deleted_at_yesterday=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_yesterday=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=24, slet_at_yesterday=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_yesterday=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=42, slet_at_yesterday=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("yesterday", client_id=user_info.user_id):.2f}$</code>'
            f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_yesterday=True) + await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_yesterday=True) + await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_yesterday=True) + await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_yesterday=True):.2f}$</code>'

            '\n\n<b>🗒 С начала недели:</b>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_week=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=17, buyed_at_week=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_week=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=18, slet_at_week=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_week=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=21, deleted_at_week=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_week=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=24, slet_at_week=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_week=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=42, slet_at_week=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("week", client_id=user_info.user_id):.2f}$</code>'
            f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_week=True) + await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_week=True) + await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_week=True) + await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_week=True):.2f}$</code>'

            '\n\n<b>🗓 С начала месяца:</b>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=17, buyed_at_month=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=18, slet_at_month=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=21, deleted_at_month=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=24, slet_at_month=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=42, slet_at_month=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("month", client_id=user_info.user_id):.2f}$</code>'
            f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True) + await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$</code>'

            '\n\n<b>↩️ С предыдущего месяца:</b>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_previous_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=17, buyed_at_previous_month=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=18, slet_at_previous_month=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=21, deleted_at_previous_month=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=24, slet_at_previous_month=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(client_id=user_info.user_id, status=42, slet_at_previous_month=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("previous_month", client_id=user_info.user_id):.2f}$</code>'
            f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(client_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(client_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True) + await select_phone_queues(client_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(client_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$</code>'
        )
    else:
        stat = (
            '\n\n<b>☀️ За сегодня:</b>'
            f'\n<b>├ Оплаченных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_00_00=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_00_00=True))})</code>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_00_00=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_00_00=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_00_00=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_00_00=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_00_00=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_00_00=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_00_00=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_00_00=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_00_00=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_00_00=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("00_00", drop_id=user_info.user_id):.2f}$</code>'
            f'\n<b>├ Убытки:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_00_00=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_00_00=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_00_00=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_00_00=True):.2f}$</code>'
            f'\n<b>└ Оплатил:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_00_00=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_00_00=True))})</code>'

            '\n\n<b>🌑 За вчера:</b>'
            f'\n<b>├ Оплаченных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_yesterday=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_yesterday=True))})</code>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_yesterday=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_yesterday=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_yesterday=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_yesterday=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_yesterday=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_yesterday=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_yesterday=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_yesterday=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_yesterday=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_yesterday=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("yesterday", drop_id=user_info.user_id):.2f}$</code>'
            f'\n<b>├ Убытки:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_yesterday=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_yesterday=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_yesterday=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_yesterday=True):.2f}$</code>'
            f'\n<b>└ Оплатил:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_yesterday=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_yesterday=True))})</code>'

            '\n\n<b>🗒 С начала недели:</b>'
            f'\n<b>├ Оплаченных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_week=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_week=True))})</code>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_week=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_week=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_week=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_week=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_week=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_week=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_week=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_week=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_week=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_week=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("week", drop_id=user_info.user_id):.2f}$</code>'
            f'\n<b>├ Убытки:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_week=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_week=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_week=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_week=True):.2f}$</code>'
            f'\n<b>└ Оплатил:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_week=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_week=True))})</code>'

            '\n\n<b>🗓 С начала месяца:</b>'
            f'\n<b>├ Оплаченных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_month=True))})</code>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_month=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_month=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_month=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_month=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_month=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("month", drop_id=user_info.user_id):.2f}$</code>'
            f'\n<b>├ Убытки:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_month=True):.2f}$</code>'
            f'\n<b>└ Оплатил:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_month=True))})</code>'
            
            '\n\n<b>↩️ С предыдущего месяца:</b>'
            f'\n<b>├ Оплаченных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, payed_amount_total=True, set_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, set_at_previous_month=True))})</code>'
            f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=17, payed_amount_total=True, buyed_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=17, buyed_at_previous_month=True))})</code>'
            f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=18, slet_at_previous_month=True))})</code>'
            f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=21, deleted_at_previous_month=True))})</code>'
            f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=24, slet_at_previous_month=True))})</code>'
            f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$ ({len(await select_phone_queues(drop_id=user_info.user_id, status=42, slet_at_previous_month=True))})</code>'
            f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("previous_month", drop_id=user_info.user_id):.2f}$</code>'
            f'\n<b>├ Убытки:</b> <code>{await select_phone_queues(drop_id=user_info.user_id, status=18, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=21, payed_amount_total=True, deleted_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=24, payed_amount_total=True, slet_at_previous_month=True) + await select_phone_queues(drop_id=user_info.user_id, status=42, payed_amount_total=True, slet_at_previous_month=True):.2f}$</code>'
            f'\n<b>└ Оплатил:</b> <code>{await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_amount_total=True, unlocked_at_previous_month=True):.2f}$ ({len(await select_phone_queues(unban_month_status=1, drop_id=user_info.user_id, unlocked_at_previous_month=True))})</code>'
        )
    return (
        '<b>👤 Информация о пользователе:</b>'
        f'\n<b>├ ID:</b> <code>{user_info.user_id}</code>'
        f'\n<b>├ Хэш:</b> <code>{user_info.user_hash}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
        f'\n<b>├ Регистрация:</b> {user_info.registered_at.strftime("%d.%m.%Y г. в %H:%M")}'
        f'\n<b>├ Автовывод:</b> <code>{"✅ вкл." if user_info.auto_withdraw_status else "выкл."}</code>'
        f'\n<b>├ Роль:</b> <code>{await get_emoji_role(user_info.role)} {user_info.role}</code>'
        f'\n<b>├ Рефевод:</b> <code>{f"/uid{user_info.referrer_id}" if user_info.referrer_id else "<code>отсутствует</code>"}</code>'
        f'\n<b>├ Стандартное значение:</b> {"" if user_info.calc_amount else "🤖 "}{(user_info.calc_amount if user_info.calc_amount else bt.main_drop_calc_amount):.2f}$'
        f'\n<b>├ Баланс:</b> {user_info.balance:.2f}$'
        f'\n<b>├ Партнёрский счёт:</b> {user_info.ref_balance:.2f}$'
        f'\n<b>├ Пригласил:</b> {await select_many_records(User, count=True, referrer_id=user_info.user_id)} чел.'
        f'\n<b>├ Заработал на рефке:</b> {await select_phone_queues(referrer_amount_total=True, referrer_id=user_info.user_id)}$'
        f'\n<b>├ Конвертировал на:</b> {await select_convert_history_writes(total_amount=True, user_id=user_info.user_id)}$'
        f'\n<b>└ Ставка:</b> {"" if user_info.ref_percent else "🤖 "}{(user_info.ref_percent if user_info.ref_percent else bt.ref_percent):.2f}%'

        f'\n\n<b>🔒 Статус:</b>'
        f'\n<b>├ Заблокирован:</b> <code>{"✅ да" if user_info.is_banned else "❌ нет"}</code> {f"(🤖 авто)" if user_info.is_banned and user_info.auto_ban_status else ""}'
        f'\n<b>└ Автоблокировка:</b> <code>{f"была ({user_info.auto_ban_count} {await decline_times(user_info.auto_ban_count)})" if user_info.auto_ban_count else "отсутствует"}</code>'

        f'{stat}'
    )

async def get_user_info_2(user_info):
    bt = await select_bot_setting()
    return (
        '<b>👤 Информация о пользователе:</b>'
        f'\n<b>├ ID:</b> <code>{user_info.user_id}</code>'
        f'\n<b>├ Хэш:</b> <code>{user_info.user_hash}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
        f'\n<b>├ Регистрация:</b> {user_info.registered_at.strftime("%d.%m.%Y г. в %H:%M")}'
        f'\n<b>├ Автовывод:</b> <code>{"✅ вкл." if user_info.auto_withdraw_status else "выкл."}</code>'
        f'\n<b>├ Роль:</b> <code>{await get_emoji_role(user_info.role)} {user_info.role}</code>'
        f'\n<b>├ Рефевод:</b> <code>{f"/uid{user_info.referrer_id}" if user_info.referrer_id else "<code>отсутствует</code>"}</code>'
        f'\n<b>├ Стандартное значение:</b> {"" if user_info.calc_amount else "🤖 "}{(user_info.calc_amount if user_info.calc_amount else bt.main_drop_calc_amount):.2f}$'
        f'\n<b>├ Баланс:</b> {user_info.balance:.2f}$'
        f'\n<b>├ Партнёрский счёт:</b> {user_info.ref_balance:.2f}$'
        f'\n<b>├ Пригласил:</b> {await select_many_records(User, count=True, referrer_id=user_info.user_id)} чел.'
        f'\n<b>├ Заработал на рефке:</b> {await select_phone_queues(referrer_amount_total=True, referrer_id=user_info.user_id)}$'
        f'\n<b>├ Конвертировал на:</b> {await select_convert_history_writes(total_amount=True, user_id=user_info.user_id)}$'
        f'\n<b>└ Ставка:</b> {"" if user_info.ref_percent else "🤖 "}{(user_info.ref_percent if user_info.ref_percent else bt.ref_percent):.2f}%'
    )

async def get_group_info(group_info):
    bt = await select_bot_setting()
    return (
        '<b>👥 Информация о группе:</b>'
        f'\n<b>├ ID:</b> <code>{group_info.group_id}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(group_info.group_name))}</code>'
        f'\n<b>├ Добавлена:</b> {group_info.created_at.strftime("%d.%m.%Y г. в %H:%M") if group_info.created_at else "отсутствует"}'
        f'\n<b>├ Ссылка:</b> {group_info.group_link if group_info.group_link else "<code>отсутствует</code>"}'
        f'\n<b>└ Стандартное значение:</b> {"" if group_info.calc_amount else "🤖 "}{(group_info.calc_amount if group_info.calc_amount else bt.main_group_calc_amount):.2f}$'

        f'\n\n<b>🔒 Статус:</b>'
        f'\n<b>├ Работает:</b> <code>{"✅ да" if group_info.work_status == 1 else "❌ нет"}</code>'
        f'\n<b>└ Ожидание слёта:</b> <code>{group_info.cross_timeout} мин.{f" или {await decline_hours_2(group_info.cross_timeout // 60)} {group_info.cross_timeout % 60} мин." if group_info.cross_timeout >= 60 else ""}</code>'

        '\n\n<b>☀️ За сегодня:</b>'
        f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=17, payed_amount_total=True, buyed_at_00_00=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_00_00=True, client_bot=0))})</code>'
        f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_00_00=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_00_00=True, client_bot=0))})</code>'
        f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_00_00=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=21, deleted_at_00_00=True, client_bot=0))})</code>'
        f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_00_00=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=24, slet_at_00_00=True, client_bot=0))})</code>'
        f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_00_00=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=42, slet_at_00_00=True, client_bot=0))})</code>'
        f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("00_00", group_id=group_info.group_id, client_bot=0):.2f}$</code>'
        f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_00_00=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_00_00=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_00_00=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_00_00=True, client_bot=0):.2f}$</code>'

        '\n\n<b>🌑 За вчера:</b>'
        f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=17, payed_amount_total=True, buyed_at_yesterday=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_yesterday=True, client_bot=0))})</code>'
        f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_yesterday=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_yesterday=True, client_bot=0))})</code>'
        f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_yesterday=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=21, deleted_at_yesterday=True, client_bot=0))})</code>'
        f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_yesterday=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=24, slet_at_yesterday=True, client_bot=0))})</code>'
        f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_yesterday=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=42, slet_at_yesterday=True, client_bot=0))})</code>'
        f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("yesterday", group_id=group_info.group_id, client_bot=0):.2f}$</code>'
        f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_yesterday=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_yesterday=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_yesterday=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_yesterday=True, client_bot=0):.2f}$</code>'

        '\n\n<b>🗒 С начала недели:</b>'
        f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=17, payed_amount_total=True, buyed_at_week=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_week=True, client_bot=0))})</code>'
        f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_week=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_week=True, client_bot=0))})</code>'
        f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_week=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=21, deleted_at_week=True, client_bot=0))})</code>'
        f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_week=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=24, slet_at_week=True, client_bot=0))})</code>'
        f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_week=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=42, slet_at_week=True, client_bot=0))})</code>'
        f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("week", group_id=group_info.group_id, client_bot=0):.2f}$</code>'
        f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_week=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_week=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_week=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_week=True, client_bot=0):.2f}$</code>'

        '\n\n<b>🗓 С начала месяца:</b>'
        f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=17, payed_amount_total=True, buyed_at_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_month=True, client_bot=0))})</code>'
        f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_month=True, client_bot=0))})</code>'
        f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=21, deleted_at_month=True, client_bot=0))})</code>'
        f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=24, slet_at_month=True, client_bot=0))})</code>'
        f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=42, slet_at_month=True, client_bot=0))})</code>'
        f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("month", group_id=group_info.group_id, client_bot=0):.2f}$</code>'
        f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_month=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_month=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_month=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_month=True, client_bot=0):.2f}$</code>'
    
        '\n\n<b>↩️ С предыдущего месяца:</b>'
        f'\n<b>├ Выданных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=17, payed_amount_total=True, buyed_at_previous_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_previous_month=True, client_bot=0))})</code>'
        f'\n<b>├ Слетевших:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_previous_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_previous_month=True, client_bot=0))})</code>'
        f'\n<b>├ Удалённых:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_previous_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=21, deleted_at_previous_month=True, client_bot=0))})</code>'
        f'\n<b>├ Невалидных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_previous_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=24, slet_at_previous_month=True, client_bot=0))})</code>'
        f'\n<b>├ Замороженных:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_previous_month=True, client_bot=0):.2f}$ ({len(await select_phone_queues(group_id=group_info.group_id, status=42, slet_at_previous_month=True, client_bot=0))})</code>'
        f'\n<b>├ Прибыль:</b> <code>{await get_total_profit("previous_month", group_id=group_info.group_id, client_bot=0):.2f}$</code>'
        f'\n<b>└ Убытки:</b> <code>{await select_phone_queues(group_id=group_info.group_id, status=18, payed_amount_total=True, slet_at_previous_month=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=21, payed_amount_total=True, deleted_at_previous_month=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=24, payed_amount_total=True, slet_at_previous_month=True, client_bot=0) + await select_phone_queues(group_id=group_info.group_id, status=42, payed_amount_total=True, slet_at_previous_month=True, client_bot=0):.2f}$</code>'
    )

async def get_group_info_2(group_info):
    bt = await select_bot_setting()
    return (
        '<b>👥 Информация о группе:</b>'
        f'\n<b>├ ID:</b> <code>{group_info.group_id}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(group_info.group_name))}</code>'
        f'\n<b>├ Добавлена:</b> {group_info.created_at.strftime("%d.%m.%Y г. в %H:%M") if group_info.created_at else "отсутствует"}'
        f'\n<b>├ Ссылка:</b> {group_info.group_link if group_info.group_link else "<code>отсутствует</code>"}'
        f'\n<b>└ Стандартное значение:</b> {"" if group_info.calc_amount else "🤖 "}{(group_info.calc_amount if group_info.calc_amount else bt.main_group_calc_amount):.2f}$'
    )


async def get_withdraw_info(withdraw):
    user_id = withdraw.user_id
    user_info = await select_user(user_id=user_id)
    amount = withdraw.amount
    amount = round(amount, 6)
    phones = withdraw.phones
    return (
        f'<b>{"❌ Отменён" if withdraw.withdraw_status == 2 else "✅ Завершён" if withdraw.withdraw_status == 1 else "⏳ Ожидание"}</b>'
        f'\n<b>├ ID:</b> <code>{user_id}</code>'
        f'\n<b>├ Имя:</b> <code>{html.bold(html.quote(user_info.fullname))}</code>'
        f'\n<b>├ Логин:</b> {f"@{user_info.username}" if user_info.username is not None else "<code>отсутствует</code>"}'
        f'\n<b>├ Создан:</b> {withdraw.created_at.strftime("%d.%m.%Y г. в %H:%M:%S") if withdraw.created_at else "<code>отсутствует</code>"}'
        f'\n<b>├ Вывод:</b> {withdraw.withdraw_at.strftime("%d.%m.%Y г. в %H:%M:%S") if withdraw.withdraw_at else "<code>отсутствует</code>"}'
        f'\n<b>├ Сумма чека:</b> <code>{amount:.2f}$</code>'
        f'\n<b>├ Чек:</b> {f"http://t.me/send?start={withdraw.check_id}" if withdraw.check_id else "<code>отсутствует</code>"}'
        f'\n<b>└ Номера:</b> {", ".join([f"<code>{phone}</code>" for phone in phones])}'
    )


async def send_message_parts(callback, text, callback_data, callback_data_back='START'):
    max_length = 4096
    if len(text) <= max_length:
        await CallbackEditText(callback=callback, text=text, reply_markup=multi_2_kb(callback_data=callback_data, callback_data_back=callback_data_back))
    else:
        parts = []
        while text:
            split_index = text.rfind('\n', 0, max_length)
            if split_index == -1 or split_index == 0:
                split_index = max_length
            part = text[:split_index]
            parts.append(part)
            text = text[split_index:].lstrip('\n')

        for i, part in enumerate(parts):
            if i == 0:
                await CallbackEditText(callback=callback, text=part, reply_markup=multi_2_kb(callback_data=callback_data, callback_data_back=callback_data_back))
            else:
                await CallbackMessageAnswer(callback, part, reply_markup=multi_kb(callback_data='DELETE', text='❌ Закрыть'))

async def send_message_parts_3(message, text, reply_markup, reply_markup_2=multi_kb(callback_data='DELETE', text='❌ Закрыть')):
    max_length = 4096
    if len(text) <= max_length:
        await MessageAnswer(message=message, text=text, reply_markup=reply_markup)
    else:
        parts = []
        while text:
            split_index = text.rfind('\n', 0, max_length)
            if split_index == -1 or split_index == 0:
                split_index = max_length
            part = text[:split_index]
            parts.append(part)
            text = text[split_index:].lstrip('\n')

        for i, part in enumerate(parts):
            if i == 0:
                await MessageAnswer(message=message, text=part, reply_markup=reply_markup)
            else:
                await MessageAnswer(message=message, text=part, reply_markup=reply_markup_2)

async def send_message_parts_4(callback, text):
    max_length = 4096
    if len(text) <= max_length:
        await CallbackMessageAnswer(callback, text, reply_markup=multi_kb(callback_data='DELETE', text='❌ Закрыть'))
    else:
        parts = []
        while text:
            split_index = text.rfind('\n', 0, max_length)
            if split_index == -1 or split_index == 0:
                split_index = max_length
            part = text[:split_index]
            parts.append(part)
            text = text[split_index:].lstrip('\n')

        for i, part in enumerate(parts):
            if i == 0:
                await CallbackMessageAnswer(callback, part, reply_markup=multi_kb(callback_data='DELETE', text='❌ Закрыть'))
            else:
                await CallbackMessageAnswer(callback, part, reply_markup=multi_kb(callback_data='DELETE', text='❌ Закрыть'))




# import phonenumbers
# from phonenumbers import carrier, geocoder


# async def validate_russian_phone(phone):
#     try:
#         cleaned = re.sub(r'[^\d+]', '', phone)
#         if cleaned.startswith('8'):
#             cleaned = '+7' + cleaned[1:]
#         elif cleaned.startswith('7'):
#             cleaned = '+' + cleaned
#         elif not cleaned.startswith('+'):
#             cleaned = '+7' + cleaned
#         parsed = phonenumbers.parse(cleaned, "RU")
#         is_valid = phonenumbers.is_valid_number(parsed)
#         is_russia = phonenumbers.region_code_for_number(parsed) == 'RU'
#         operator = carrier.name_for_number(parsed, 'ru')
#         return all([is_valid, is_russia, operator != ''])
#     except Exception:
#         return False
