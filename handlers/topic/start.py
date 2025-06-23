from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from utils.additionally_bot import *


router = Router()


@router.message(CommandStart(ignore_case=True))
async def start_command(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await MessageAnswer(
        message,
        text=(
            f'\n\n<b>🆔 ID топика:</b> <code>{message.chat.id}</code>'
        )
    )

# @router.message()
# async def message_handler(message: Message, bot: Bot):
#     print(message)
#     print(message.html_text)
#     print(message.text)