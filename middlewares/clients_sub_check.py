from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Update

from database.commands.users import *
from database.commands.bot_settings import *

from keyboards.inline.misc_kb import subscribe_kb

from utils.additionally_bot import *

from config import *


class ClientsSubCheckMiddleware(BaseMiddleware):
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
                if bot.id == int(SECOND_BOT_TOKEN.split(':')[0]):
                    bt = await select_bot_setting()
                    if bt.op_client_channel_id and bt.op_client_channel_link:
                        usr = await select_user(user_id=user.id)
                        if chat and chat.type == ChatType.PRIVATE and message and usr:
                            try:
                                member = await BotGetChatMember(bot, chat_id=bt.op_client_channel_id, user_id=user.id)
                                # print(member)
                                if member and member.status not in ('member', 'administrator', 'creator'):
                                    return await MessageAnswer(
                                        message,
                                        text=f'<b>❗️ Подпишитесь на наш <a href="{bt.op_client_channel_link}">канал</a>, чтобы продолжить.</b>',
                                        reply_markup=subscribe_kb(bt.op_client_channel_link),
                                        disable_web_page_preview=True
                                    )
                            except:
                                traceback.print_exc()
        return await handler(event, data)

