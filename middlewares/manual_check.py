from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Update

from database.commands.users import *
from database.commands.bot_settings import *

from keyboards.inline.misc_kb import manual_check_kb

from utils.additionally_bot import *

from config import *

class ManualCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        bot = data['bot']
        message = None
        user = None
        chat = None
        if event:
            if hasattr(event, 'message') and event.message:
                message = event.message
                user = message.from_user
                chat = message.chat
            elif hasattr(event, 'callback_query') and event.callback_query:
                message = event.callback_query.message
                user = message.from_user
                chat = message.chat
            elif hasattr(event, 'edited_message') and event.edited_message:
                message = event.edited_message
                user = message.from_user
                chat = message.chat
        if user:
            bot = data.get('bot')
            if bot:
                if bot.id == int(BOT_TOKEN.split(':')[0]):
                    bt = await select_bot_setting()
                    if bt.manual_status and bt.manual_link:
                        usr = await select_user(user_id=user.id)
                        if chat and chat.type == ChatType.PRIVATE and message and usr and usr.role == 'drop' and usr.manual_read_status == 0:
                            try:
                                return await MessageAnswer(
                                    message,
                                    text=f'<b>❗️ Прочитайте актуальную <a href="{bt.manual_link}">инструкцию</a>, чтобы продолжить.</b>',
                                    reply_markup=manual_check_kb(bt.manual_link),
                                    disable_web_page_preview=True
                                )
                            except:
                                traceback.print_exc()
        return await handler(event, data)

