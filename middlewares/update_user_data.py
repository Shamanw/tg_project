import random
import asyncio

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.tables import User
from database.commands.main import *
from database.commands.users import *

from keyboards.inline.misc_kb import *

from utils.misc import generate_random_code
from utils.additionally_bot import *

from config import *


class UpdateUserDataMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        user = None
        if event:
            if hasattr(event, 'message') and event.message:
                message = event.message
                user = event.message.from_user
            elif hasattr(event, 'callback_query') and event.callback_query:
                message = event.callback_query.message
                user = event.callback_query.from_user
            elif hasattr(event, 'edited_message') and event.edited_message:
                message = event.edited_message
                user = event.edited_message.from_user
        user_info = None
        if user:
            bot = data.get('bot')
            if bot:
                if bot.id == int(SECOND_BOT_TOKEN.split(':')[0]):
                    if hasattr(event, 'message') and event.message:
                        text = event.message.text if hasattr(event.message, 'text') else None
                        if text and text.strip().startswith('/start'):
                            return await handler(event, data)
                        user_id = user.id
                        user_info = await select_user(user_id=user_id)
                        if not user_info:
                            await asyncio.sleep(random.uniform(0.000001, 0.0009))
                            await add_record(
                                User,
                                user_id=user_id,
                                user_hash=await generate_random_code(),
                                referrer_id=None,
                                fullname=f'{user.first_name} {user.last_name if user.last_name else ""}'.strip(),
                                username=user.username,
                                registered_at=datetime.now(),
                                clients_reg_status=1
                            )
                        elif user_info.clients_reg_status == 0:
                            await update_record(
                                User,
                                user_id=user_id,
                                data={
                                    User.clients_reg_status: 1,
                                    User.user_hash: await generate_random_code() if user_info.user_hash is None else user_info.user_hash
                                }
                            )
                    return await handler(event, data)
                user_fullname = f'{user.first_name} {user.last_name if user.last_name else ""}'.strip()
                user_info = await select_user(user_id=user.id)
                if not user_info:
                    await asyncio.sleep(random.uniform(0.000001, 0.0009))
                    if not await select_user(user_id=user.id):
                        await add_user(user_id=user.id, fullname=user_fullname, username=user.username)
                        # if not await select_allow_search_phone_type(user_id=user.id):
                        #     await add_allow_search_phone_type(user_id=user.id)
                else:
                    await update_user(
                        user_id=user.id,
                        data={
                            User.fullname: user_fullname if user_fullname else user_info.fullname,
                            User.username: user.username if user.username else user_info.username
                        }
                    )
        if user and user_info and user_info.is_banned:
            if hasattr(event, 'message') and event.message:
                return await MessageAnswer(
                    message,
                    text=(
                        '<b>⛔️ Вы заблокированы в боте по одной из следующих причин:</b> большое количество невалидных/слетевших аккаунтов, нарушение правил бота или другие причины.'
                    ),
                    reply_markup=multi_2_kb(
                        text='Посмотреть статистику номеров', callback_data='SLET|M',
                        text_back='Купить разбан', callback_data_back='UNBAN|M',
                    ),
                    disable_web_page_preview=True
                )
            # return None
        return await handler(event, data)

