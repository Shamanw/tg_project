from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from database.commands.groups import *

from utils.additionally_bot import *

router = Router()


@router.message(CommandStart(ignore_case=True))
async def start_command(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    group_id = message.chat.id
    group_info = await select_group(group_id=group_id)
    await MessageReply(
        message,
        f'<b>🆔 ID группы:</b> <code>{group_id}</code>'
        f'\n{"<b>✅ Статус:</b> <code>группа добавлена или включена</code>" if group_info and group_info.work_status == 1 else "<b>❌ Статус:</b> <code>группа не добавлена или выключена</code>"}'
        '\n\n<b>⬇️ Команды/Триггеры:</b>'
        '\n\n<b>📱 Получить телеграм:</b>'
        '\n├ <code>тг</code>'
        '\n├ <code>tg</code>'
        '\n└ /tg'
        '\n\n<b>📊 Статистика:</b>'
        '\n├ <code>стата</code>'
        '\n├ <code>статистика</code>'
        '\n├ <code>stats</code>'
        '\n└ /stats'
        '\n\n<b>➕ Добавить группу:</b> /gadd | /tadd'
        '\n<b>➖ Удалить группу:</b> /gdel | /tdel'
    )

