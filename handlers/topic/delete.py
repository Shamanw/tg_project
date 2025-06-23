from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, Union
from aiogram.fsm.context import FSMContext

from utils.additionally_bot import BotDeleteMessage

router = Router()

@router.callback_query(F.data == 'DELETE')
async def delete_message_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await BotDeleteMessage(bot, chat_id=callback.message.chat.id, message_id=callback.message.message_id)
