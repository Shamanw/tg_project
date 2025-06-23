import traceback
from aiogram import Router, F
from aiogram.types import Message
from utils.additionally_bot import BotDeleteMessage

boost_router = Router()

@boost_router.message(lambda message: hasattr(message, 'boost_added') and message.boost_added)
async def handle_boost_added(message: Message, bot):
    try:
        chat_id = message.chat.id
        message_id = message.message_id
        # boost_count = message.boost_added.get('boost_count', 0)
        await BotDeleteMessage(bot, chat_id=chat_id, message_id=message_id)
    except Exception as e:
        traceback.print_exc()
        print(f"Ошибка при обработке сообщения о бусте: {e}")
