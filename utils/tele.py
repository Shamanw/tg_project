import os
import re
import time
import json
import random
import string
import shutil
import aiohttp
import zipfile
import asyncio
import logging
import traceback

from aiogram import html
from aiogram.exceptions import TelegramRetryAfter

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from TGConvertor.manager import SessionManager, API
from python_socks._errors import ProxyError


from asyncio import IncompleteReadError
from aiohttp import ClientSession, ClientConnectionError, ClientSSLError, ClientError, http_exceptions
from aiohttp_socks import ProxyConnector, ProxyError, ProxyConnectionError
# from python_socks._errors import ProxyConnectionError

from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

from telethon.errors import (
    FloodWaitError, 
    PhoneNumberInvalidError, SessionPasswordNeededError,
    PhoneNumberBannedError, PhoneNumberUnoccupiedError,
    PhoneCodeExpiredError, PhoneCodeInvalidError,
    PasswordHashInvalidError
)

from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact


from aiohttp import ClientConnectionError, ClientSSLError, ClientError
from aiohttp_socks import ProxyError, ProxyConnectionError
from python_socks._errors import ProxyError



from keyboards.inline.misc_kb import *

from database.commands.proxy_socks_5 import *
from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from database.commands.bot_settings import *

from utils.misc import check_proxy
from utils.additionally_bot import *

from config import *

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired, FloodWait, RPCError, AuthKeyUnregistered
from pyrogram.raw.functions.account import GetAuthorizations
from pyrogram.raw.types import EmailVerifyPurposeLoginSetup, EmailVerificationCode
from pyrogram.errors import EmailUnconfirmed



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')


api_id = 22213598
api_hash = 'f9af4a44e3b25440580f3c6853393694'
__device_model__ = "A320MH"
__system_version__ = "4.16.30-vxEmby"
__app_version__ = "7.2.0"


API_IDS = [27011010, 23785846, 22213598, api_id,]
API_HASHS = ['7bf4228fbc11a8b88c91556dffb5186e', 'bd740ea2acee7390e0b354ec809c870f', 'f9af4a44e3b25440580f3c6853393694', api_hash,]


async def proccess_phone(phone):
    for _ in ['+', '-', '(', ')', '/', '.', ',', ' ']:
        phone = phone.replace(_, '')
    return phone


async def send_auth_code(phone, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(phone))
        session_name = f'{phone}_{int(time.time())}'

        # if not await check_proxy(proxy):
        #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
        #     return None, 'proxy_error'
        
        logger.info(f'[send_auth_code] phone: {phone}, session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        sent = await client.send_code_request(phone=phone)
        if sent and sent.phone_code_hash:
            logger.info(f'[{phone} > conn:{is_connected}] [send_code_request] {sent}')
            return session_name, sent.phone_code_hash
        else:
            func_error = 'send_error'
            print_error = 'Не удалось отправить код'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def enter_auth_code(write, code, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name
        phone_code_hash = write.phone_code_hash

        # if not await check_proxy(proxy):
        #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
        #     return None, 'proxy_error'
        
        logger.info(f'[enter_auth_code] session_name: {session_name}, phone_code_hash: {phone_code_hash}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        auth = await client.sign_in(phone=phone, code=int(code), phone_code_hash=phone_code_hash)
        if auth:
            logger.info(f'[{phone} > conn:{is_connected}] [sign_in] {auth}')
            # return True, True
            return True, True
        else:
            func_error = 'sign_in_error'
            print_error = 'Не удалось авторизоваться'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PhoneCodeInvalidError:
        func_error = 'invalid_code'
        print_error = 'Введен неверный код авторизации'

    except PhoneCodeExpiredError:
        func_error = 'code_expired'
        print_error = 'Код авторизации истёк'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def send_message_for_check_spam(write, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name

        logger.info(f'[send_message_for_check_spam] session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )
        random_1 = str(random.randint(1000000, 999999999))
        random_2 = str(random.randint(1000000, 999999999))
        message_text = f'Hello x{random_1}{random_2}{int(time.time())}x!'
        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            logger.info(f'Отправка сообщения {message_text} на {phone}')
            entity = '@texprnc'
            sent_message = await client.send_message(entity, message_text)
            logger.info(f'Сообщение отправлено на {phone}, response: {sent_message}')
            await asyncio.sleep(0.5)
            if sent_message and sent_message.id:
                await client.delete_messages(entity, [sent_message.id])
                logger.info(f'Сообщение удалено с {phone}, ID: {sent_message.id}')
                try:
                    await client.delete_dialog(entity)
                except:
                    pass
                logger.info(f'[{phone} > conn:{is_connected}] [send_message_for_check_spam] SUCCESS')
                return True, True
            else:
                func_error = 'send_message_for_check_spam_error'
                print_error = 'Не удалось отправить сообщение'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    # except PasswordAlreadySetError:
    #     # func_error = 'password_already_set'
    #     print_error = 'Пароль уже установлен'

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PasswordHashInvalidError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    except Exception as e:
        if 'Too many requests' in str(e):
            func_error = 'spam_block'
            print_error = f'[{phone}] Spamblock: {str(e)}'
        elif 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.error(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def check_shadow_ban(write, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name

        logger.info(f'[check_shadow_ban] session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )
        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            logger.info(f'Добавление в контакты на {phone}')
            contact_phone = '79856034081'
            input_contact = InputPhoneContact(client_id=0, phone=contact_phone, first_name="Friend", last_name=f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(100, 999)}")
            result = await client(ImportContactsRequest(contacts=[input_contact]))
            if result.users:
                user = result.users[0]
                user_id = user.id
                if user_id:
                    print(f"Контакт добавлен на {phone}. ID пользователя: {user_id}")
                    try:
                        await client(DeleteContactsRequest(id=[user]))
                    except:
                        pass
                    logger.info(f'[{phone} > conn:{is_connected}] [shadow_ban] SUCCESS')
                    return True, True
                else:
                    func_error = 'check_shadow_ban_error'
                    print_error = 'Не удалось получить айди пользователя'
            else:
                func_error = 'check_shadow_ban_error'
                print_error = 'Не удалось добавить в контакты'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    # except PasswordAlreadySetError:
    #     # func_error = 'password_already_set'
    #     print_error = 'Пароль уже установлен'

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PasswordHashInvalidError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    except Exception as e:
        if 'Too many requests' in str(e):
            func_error = 'shadow_ban'
            print_error = f'[{phone}] Shadow BAN: {str(e)}'
        elif 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.error(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None
    

async def enable_2fa(write, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name

        # if not await check_proxy(proxy):
        #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
        #     return None, 'proxy_error'
        
        logger.info(f'[enable_2fa] session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        password = str(random.randint(1000, 9999))
        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            logger.info(f'Установка пароля {password} на {phone}')
            # await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: password})
            try:
                await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: password})
            except:
                traceback.print_exc()
                try:
                    await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: password})
                except:
                    traceback.print_exc()
                    await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: password})
            await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: password})
            resp = await client.edit_2fa(new_password=password, hint='CODE')
            logger.info(f'Установка пароля {phone}, ответ: {resp}')
            if resp:
                logger.info(f'Установка пароля {phone} (UPDATED)')
                logger.info(f'[{phone} > conn:{is_connected}] [edit_2fa] {resp}')
                # return True, True
                return True, True
            else:
                func_error = 'edit_2fa_error'
                print_error = 'Не удалось установить пароль'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    # except PasswordAlreadySetError:
    #     # func_error = 'password_already_set'
    #     print_error = 'Пароль уже установлен'

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except PasswordHashInvalidError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except Exception as e:
        if 'The password (and thus its hash value) you entered is invalid (caused by UpdatePasswordSettingsRequest)' in str(e):
            if write.password is not None:
                try:
                    await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: write.password})
                except:
                    traceback.print_exc()
                    try:
                        await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: write.password})
                    except:
                        traceback.print_exc()
                        await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: write.password})
                await update_phone_queue(primary_id=write.id, data={PhoneQueue.password: write.password})
                return True, True
        # if 'There is already a cloud password enabled' in str(e):
        #     print_error = f'DAUSDIUASDIJASIKDJASJIKDAJSIKDJKAS: {str(e)}'
        # else:
        elif 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.error(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def delete_2fa(write, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name

        # if not await check_proxy(proxy):
        #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
        #     return None, 'proxy_error'
        
        logger.info(f'[delete_2fa] session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            resp = await client.edit_2fa(current_password=write.password, new_password=None)
            if resp:
                logger.info(f'[{phone} > conn:{is_connected}] [delete_2fa] {resp}')
                # return True, True
                return True, True
            else:
                func_error = 'delete_2fa_error'
                print_error = 'Не удалось удалить пароль'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    # except PasswordAlreadySetError:
    #     # func_error = 'password_already_set'
    #     print_error = 'Пароль уже установлен'

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except Exception as e:
        # if 'There is already a cloud password enabled' in str(e):
        #     print_error = f'DAUSDIUASDIJASIKDJASJIKDAJSIKDJKAS: {str(e)}'
        # else:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def check_sessions(write, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name

        # if not await check_proxy(proxy):
        #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
        #     return None, 'proxy_error'
  
        logger.info(f'\n\n[check_sessions] session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            sessions = await client(functions.account.GetAuthorizationsRequest())
            if sessions:
                for session in sessions.authorizations:
                    logger.info(f'[check_sessions] session_name: {session_name}, device: {session}')
                    # logger.info(session.api_id)
                    if session.api_id not in API_IDS:
                        # logger.info(None, None)
                        return None, None
                    # if session.device_model != 'Samsung SM-S931B' or session.platform != 'Android' or session.system_version != '15 (35)':
                        # return False, False
                return True, True
            else:
                func_error = 'check_sessions_error'
                print_error = 'Не удалось получить сессии'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except PhoneNumberInvalidError:
        func_error = 'invalid_phone'
        print_error = 'Неверный номер телефона'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    # except PasswordAlreadySetError:

    except PhoneNumberBannedError:
        func_error = 'phone_banned'
        print_error = 'Номер телефона заблокирован'

    except PhoneNumberUnoccupiedError:
        func_error = 'phone_unregistered'
        print_error = 'Номер телефона не зарегистрирован в Telegram'

    except Exception as e:
        # if 'There is already a cloud password enabled' in str(e):
        #     print_error = f'DAUSDIUASDIJASIKDJASJIKDAJSIKDJKAS: {str(e)}'
        # else:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None



def extract_code(text):
    match = re.search(r'\b\d{5,6}\b', text)
    if match:
        return match.group(0)
    return None

async def get_42777_code(write, proxy):
    try:
        func_error = None
        print_error = ''
        is_connected = False
        phone = str(await proccess_phone(write.phone_number))
        session_name = write.session_name

        # if not await check_proxy(proxy):
        #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
        #     return None, 'proxy_error'
  
        logger.info(f'[get_42777_code] session_name: {session_name}, proxy: {proxy}')
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            async for msg in client.iter_messages(777000, limit=1):
                code = extract_code(msg.text)
                if code:
                    return True, code
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        func_error = f'flood_wait|{e.seconds}'
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def validate_session(write, proxy):
    func_error = None
    print_error = ''
    is_connected = False
    phone = str(await proccess_phone(write.phone_number))
    session_name = write.session_name

    # if not await check_proxy(proxy):
    #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
    #     return None, 'proxy_error'

    # logger.info(f'[validate_session] phone: {write.phone_number}, session_name: {session_name}, proxy: {proxy}')
    try:
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            get_me = await client.get_me()
            # print(f'SESSION: {session_name} | get_me: {get_me}')
            if get_me and get_me.id:
                return True, True
            else:
                func_error = 'not_auth'
                print_error = 'Пользователь не авторизован'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def account_is_frozen_status(write, proxy):
    func_error = None
    print_error = ''
    is_connected = False
    phone = str(await proccess_phone(write.phone_number))
    session_name = write.session_name

    # if not await check_proxy(proxy):
    #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
    #     return None, 'proxy_error'

    # logger.info(f'[validate_session] phone: {write.phone_number}, session_name: {session_name}, proxy: {proxy}')
    try:
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )

        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            get_me = await client(functions.users.GetFullUserRequest(id='me'))
            print(f'SESSION: {session_name} | get_me: {get_me}')
            if (hasattr(get_me.full_user, 'bot_verification') and get_me.full_user.bot_verification and 'frozen' in get_me.full_user.bot_verification.description.lower()):
                # print("Аккаунт заморожен!")
                return True, True
            else:
                func_error = 'not_auth'
                print_error = 'Пользователь не авторизован'
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
            return True, True
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{phone} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None


async def proccessing_session_for_tdata_adder(session_name, proxy):
    func_error = None
    print_error = ''
    is_connected = False
    # if not await check_proxy(proxy):
    #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
    #     return None, 'proxy_error'
    logger.info(f'[get_session] session_name: {session_name}, proxy: {proxy}')
    logger.info(f'sessions_base/{session_name}.session')
    try:
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=10,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )
        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            get_me = await client.get_me()
            return True, get_me
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{session_name} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None

async def get_session_for_tdata_adder(session_name, proxy):
    max_attempts = 3
    resp1 = None; resp2 = None
    for attempt in range(max_attempts):
        resp1, resp2 = await proccessing_session_for_tdata_adder(session_name=session_name, proxy=proxy)
        print(f'Попытка {attempt + 1}: resp1: {resp1} | {type(resp2)} resp2: {resp2}')
        if resp1 and resp2 and resp2.phone:
            return resp1, resp2
    else:
        return resp1, resp2


async def terminate_all_sessions(write, proxy=None):
    if not proxy and write:
        proxy = write.auth_proxy
        if proxy:
            proxy = {
                "scheme": proxy['scheme'],
                "hostname": proxy['hostname'],
                "port": int(proxy['port']),
                "username": proxy['username'],
                "password": proxy['password']
            }
        if not proxy or (proxy and not await check_proxy(proxy=proxy)):
            proxy = await select_proxy_socks_5()
            if proxy:
                proxy = {
                    'scheme': proxy.scheme,
                    'hostname': proxy.ip,
                    'port': int(proxy.port),
                    'username': proxy.login,
                    'password': proxy.password
                }
            if not proxy or (proxy and not await check_proxy(proxy=proxy)):
                return None, None
    if not proxy:
        return None, None
    
    func_error = None
    print_error = ''
    is_connected = False
    # if not await check_proxy(proxy):
    #     logger.info(f'[{phone} > conn:{is_connected}] [proxy_error] Невалидный прокси: {proxy}')
    #     return None, 'proxy_error'
    session_name = write.session_name
    logger.info(f'[terminate_all_sessions] session_name: {session_name}, proxy: {proxy}')
    logger.info(f'sessions_base/{session_name}.session')
    try:
        client = TelegramClient(
            session=f'sessions_base/{session_name}',
            api_id=api_id,
            api_hash=api_hash,
            proxy=(proxy['scheme'], proxy['hostname'], int(proxy['port']), True, proxy['username'], proxy['password']),
            device_model=__device_model__,
            system_version=__system_version__,
            app_version=__app_version__,
            #lang_code='jabka',
            auto_reconnect=False,
            timeout=15,
            request_retries=2,
            connection_retries=2,
            retry_delay=1,
        )
        await client.connect()
        is_connected = True
        if await client.is_user_authorized():
            logger.info(f'[terminate_all_sessions] session_name: {session_name}, processing..') 
            sessions = await client(functions.account.GetAuthorizationsRequest())
            if sessions and sessions.authorizations:
                for auth in sessions.authorizations:
                    # print(f'\n\n\ndevice: {auth}')
                    if auth.api_id not in API_IDS:
                        # print(f'\nKICK: {auth.api_id}')
                        await client(functions.account.ResetAuthorizationRequest(hash=auth.hash))
            logger.info(f'[terminate_all_sessions] session_name: {session_name}, done')
            return True, True
        else:
            func_error = 'not_auth'
            print_error = 'Пользователь не авторизован'

    except FloodWaitError as e:
        print_error = f'Словлен FloodWait, до снятия {e.seconds} сек.'

    except (OSError, ConnectionError) as e:
        # func_error = 'connection_error'
        print_error = 'Ошибка подключения'

    except IncompleteReadError as e:
        # func_error = 'incomplete_read_error'
        print_error = 'Неполное чтение данных (плохое соединение)'

    except SessionPasswordNeededError:
        func_error = 'password_needed'
        print_error = 'Требуется пароль'

    except Exception as e:
        if 'FROZEN_METHOD_INVALID' in str(e):
            func_error = 'frozen_method_invalid'
            print_error = 'Аккаунт заморожен'
        else:
            traceback.print_exc()
            # func_error = 'unexpected_error'
            print_error = f'Неизвестная ошибка: {str(e)}'
    finally:
        if is_connected:
            try:
                await client.disconnect()
            except:
                pass
    logger.info(f'[{session_name} > conn:{is_connected}] [{func_error}] {print_error}')
    if func_error is not None:
        return False, func_error
    else:
        return None, None















