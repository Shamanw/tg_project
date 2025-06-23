import time
import random
import asyncio

from aiogram import Bot, Router, F, html
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from datetime import datetime
from collections import defaultdict

from database.commands.users import *
from database.commands.groups import *
from database.commands.phones_queue import *
from utils.misc import *
from utils.additionally_bot import *
# from utils.misc import different_time, get_phone_type_text, get_phone_type_emoji, get_phones_queue_status_type, get_phone_queue, get_phones_queue, find_inds

from config import *

router = Router()
record_locks = defaultdict(asyncio.Lock)
group_photo_locks = defaultdict(asyncio.Lock)
group_record_locks = defaultdict(asyncio.Lock)
group_record_locks2 = defaultdict(asyncio.Lock)


# async def update_group_info(bot, message):
#     try:
#         group_id = message.chat.id
#         group_info = await select_group(group_id=group_id)
#     except:
#         group_info = None
#     if group_info:
#         try:
#             if not group_info.group_link or group_info.group_name != message.chat.title:
#                 await update_group(
#                     group_id=group_id,
#                     data={
#                         Group.group_name: message.chat.title,
#                         Group.group_link: (await bot.create_chat_invite_link(chat_id=group_id)).invite_link if not group_info.group_link else Group.group_link,
#                         Group.updated_at: datetime.now()
#                     }
#                 )
#         except:
#             try:
#                 if group_info.group_name != message.chat.title:
#                     await update_group(group_id=group_id, data={Group.group_name: message.chat.title, Group.updated_at: datetime.now()})
#             except:
#                 pass


# @router.callback_query(F.data.startswith('QUEUE'))
# async def group_queue_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):
#     await state.clear()
#     group_id = callback.message.chat.id
#     group_info = await select_group(group_id=group_id)
#     if group_info and group_info.work_status == 1:
#         await update_group_info(bot, callback.message)
#         callback_data = callback.data.split('|')
#         action = callback_data[1]
#         primary_id = int(callback_data[2])
#         lock = record_locks[primary_id]
#         async with lock:
#             await asyncio.sleep(random.uniform(0.5, 0.9))
#             write = await select_phone_queue(primary_id=primary_id)
#             if not write:
#                 return await CallbackAnswer(callback, text='⚠️ Запись не найдена!', show_alert=True)
#             if write.client_id is None:
#                 return await CallbackAnswer(callback, text='⚠️ Запись недоступна!', show_alert=True)
#             if write.client_id != callback.from_user.id and callback.from_user.id != ADMIN_ID:
#                 return await CallbackAnswer(callback, text='⛔️ Данный номер принадлежит другому пользователю, вы не можете с ним взаимодействовать!')

#             if action == 'SMS':
#                 if write.status != 14:
#                     return await CallbackAnswer(callback, text='🚫 Данная запись больше недействительна!', show_alert=True)
#                 else:
#                     await update_phone_queue(
#                         primary_id=write.id,
#                         data={
#                             PhoneQueue.status: 15,
#                             PhoneQueue.updated_at: datetime.now()
#                         }
#                     )
#                     await CallbackEditText(
#                         callback,
#                         text=(
#                             f'<b>⏳ Получение кода:</b> <code>{write.phone_number}</code>'
#                             f'\n\n<b>❗️ Отправьте код на указанный номер, у вас есть 5 минут!</b>'
#                             f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
#                         ),
#                         reply_markup=None
#                         # reply_markup=multi_kb(
#                         #     text='✅', callback_data=f'QUEUE|SCCS|{write.id}',
#                         # )
#                     )

#             # elif action == 'SCCS':
#             #     if write.status != 15:
#             #         return await CallbackAnswer(callback, text='🚫 Данная запись больше недействительна!', show_alert=True)
#             #     else:
#             #         await update_phone_queue(
#             #             primary_id=write.id,
#             #             data={
#             #                 PhoneQueue.status: 17,
#             #                 PhoneQueue.updated_at: datetime.now(),
#             #                 PhoneQueue.buyed_at: datetime.now(),
#             #                     calc_amount
#             #             }
#             #         )
#             #         await CallbackEditText(
#             #             callback,
#             #             text=(
#             #                 f'<b>✅ Подтверждён:</b> <code>{write.phone_number}</code>'
#             #                 f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
#             #                 f'\n<b>✉️ Код:</b> <code>{write.last_auth_code}</code>'
#             #                 f'<a href="tg://sql?write_id={write.id}">\u2063</a>'
#             #             ),
#             #             reply_markup=None
#             #         )


# @router.message()
# async def message_handler(message: Message, bot: Bot):
#     group_id = message.chat.id
#     try:
#         sent_message = message.text.strip().replace(' ', '').lower()
#     except:
#         sent_message = False
#     if sent_message:
#         group_info = await select_group(group_id=group_id)
#         if sent_message.startswith('/gadd') or sent_message.startswith('/tadd'):
#             user_info = await select_user(user_id=message.from_user.id)
#             if user_info.role == 'admin' or message.from_user.id == ADMIN_ID:
#                 group_info = await select_group(group_id=group_id)
#                 if not group_info:
#                         try:
#                             group_name = (await bot.get_chat(chat_id=group_id)).title
#                         except:
#                             group_name = None
#                         try:
#                             group_link = (await bot.create_chat_invite_link(chat_id=group_id)).invite_link
#                         except:
#                             group_link = None
#                         await add_group(group_id=group_id, group_link=group_link, group_name=group_name)
#                         await MessageReply(message, text='<b>✅ Группа успешно добавлена!</b>')
#                 elif group_info and group_info.work_status == 0:
#                     await update_group(group_id=group_id, data={Group.work_status: 1})
#                     await MessageReply(message, text='<b>✅ Группа успешно добавлена!</b>')
#                 else:
#                     await MessageReply(message, text='<b>❌ Данная группа уже добавлена!</b>')
#             else:
#                 await MessageReply(message, text='<b>⛔️ Недостаточно прав для добавления группы!</b>')
#         elif sent_message.startswith('/gdel') or sent_message.startswith('/tdel'):
#             user_info = await select_user(user_id=message.from_user.id)
#             if user_info.role == 'admin' or message.from_user.id == ADMIN_ID:
#                 group_info = await select_group(group_id=group_id)
#                 user_info = await select_user(user_id=message.from_user.id)
#                 if group_info and group_info.work_status == 1:
#                     await update_group(group_id=group_id, data={Group.work_status: 0})
#                     await MessageReply(message, text='<b>🗑 Группа успешно удалена!</b>')
#                 elif group_info and group_info.work_status == 0:
#                     await MessageReply(message, text='<b>❌ Данная группа уже удалена!</b>')
#                 else:
#                     await MessageReply(message, text='<b>❌ Группа не добавлена в базу!</b>')
#             else:
#                 await MessageReply(message, text='<b>⛔️ Недостаточно прав для удаления группы!</b>')
#         else:
#             if group_info and group_info.work_status == 1:
#                 await update_group_info(bot, message)
#                 if sent_message == 'tg' or sent_message == 'тг' or sent_message.startswith('/tg') or sent_message.startswith('/telegram'):
#                     lock = group_record_locks[group_id]
#                     async with lock:
#                         bt = await select_bot_setting()
#                         if bt.get_phones_status == 0:
#                             return await MessageReply(
#                                 message,
#                                 text=(
#                                     f'<b>⚠️ На данный момент выдача номеров выключена, запросите команду ещё раз немного позже!</b>'
#                                 )
#                             )

#                         write = await select_phone_queue(status=12)
#                         if not write:
#                             await MessageReply(
#                                 message,
#                                 text=(
#                                     f'<b>⚠️ На данный момент нет доступных номеров, запросите команду ещё раз немного позже!</b>'
#                                 )
#                             )
#                         else:
#                             await update_phone_queue(
#                                 primary_id=write.id,
#                                 data={
#                                     PhoneQueue.client_id: message.from_user.id,
#                                     PhoneQueue.group_id: group_id,
#                                     PhoneQueue.status: 14,
#                                     PhoneQueue.group_user_message_id: message.message_id,
#                                     PhoneQueue.updated_at: datetime.now(),
#                                 }
#                             )
#                             response = await MessageReply(
#                                 message,
#                                 text=(
#                                     f'<b>📱 Номер:</b> <code>{write.phone_number}</code>'
#                                     '\n\n<b>❗️ У вас есть две минуты для ответа!</b>'
#                                 ),
#                                 reply_markup=multi_kb(
#                                     text='📩 Получить код', callback_data=f'QUEUE|SMS|{write.id}'
#                                 )
#                             )   
#                             await update_phone_queue(
#                                 primary_id=write.id,
#                                 data={
#                                     PhoneQueue.group_bot_message_id: response.message_id,
#                                 }
#                             )

#                 elif (sent_message in ['слет', 'слёт', 'slet'] or sent_message.startswith('/slet')) and \
#                     message.reply_to_message and \
#                     message.reply_to_message.from_user.id == bot.id:
#                     # print(message.reply_to_message)
#                 # elif sent_message == 'слет' or sent_message == 'слёт' or sent_message == 'slet' or sent_message.startswith('/slet') and message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
#                     primary_id = await extract_write_id(text=message.reply_to_message.html_text)
#                     if primary_id:
#                         lock = group_record_locks2[primary_id]
#                         async with lock:
#                             write = await select_phone_queue(primary_id=primary_id)
#                             if write:
#                                 group_info = await select_group(group_id=write.group_id)
#                                 if group_info:
#                                     # if await different_time(write.get_sms_at, group_info.cross_timeout if write.phone_type == 0 else group_info.cross_timeout_tg) and write.get_sms_status != 6 and write.get_sms_status != 12 and write.get_sms_status != 3 and write.get_sms_status != 17:
#                                     if (group_info and not await different_time(write.updated_at, group_info.cross_timeout) and write.status in [15, 17]) or message.from_user.id == ADMIN_ID:
#                                         if write.status == 15:
#                                             await MessageReply(message=message, text=f'<b>⛔️ Команда слёт доступна только после подтверждения номера!</b>')
#                                         elif write.status == 17:
#                                             await update_phone_queue(primary_id=write.id, data={PhoneQueue.status: 18, PhoneQueue.slet_at: datetime.now()})
#                                             await MessageReply(
#                                                 message, 
#                                                 text=(
#                                                     f'<b>💢 Слёт (-1)</b>'
#                                                 )
#                                             )
#                                             if write.group_bot_message_id:
#                                                 await BotEditText(
#                                                     bot,
#                                                     chat_id=group_id,
#                                                     message_id=write.group_bot_message_id,
#                                                     text=(
#                                                         f'<b>💢 Слёт (-1):</b> <code>{write.phone_number}</code>'
#                                                         f'\n<b>🔑 Пароль:</b> <code>{write.password}</code>'
#                                                         f'\n<b>✉️ Код:</b> <code>{write.last_auth_code}</code>'
#                                                     )
#                                                 )
#                                     else:
#                                         await MessageReply(message=message, text=f'<b>⛔️ Данная запись недействительна!</b>')
#                                 else:
#                                     await MessageReply(message=message, text=f'<b>⛔️ Группа не подключена!</b>')
#                             else:
#                                 await MessageReply(message=message, text=f'<b>⛔️ Запись не найдена!</b>')
#                     else:
#                         await MessageReply(message=message, text=f'<b>⛔️ Запись не найдена!</b>')


#                 elif sent_message == 'стата' or sent_message == 'статистика' or sent_message == 'stats' or sent_message.startswith('/stats'):
#                     group_info = await select_group(group_id=group_id)
#                     if not group_info:
#                         return await MessageReply(message, '<b>⚠️ Группа отсутствует в базе!</b>')
#                     await MessageAnswer(
#                         message,
#                         text=(
#                             '\n\n<b>☀️ За сегодня:</b>'
#                             f'\n<b>├ Выданных:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_00_00=True))}</code>'
#                             f'\n<b>└ Слетевших:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_00_00=True))}</code>'

#                             '\n\n<b>🌑 За вчера:</b>'
#                             f'\n<b>├ Выданных:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_yesterday=True))}</code>'
#                             f'\n<b>└ Слетевших:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_yesterday=True))}</code>'

#                             '\n\n<b>🗒 С начала недели:</b>'
#                             f'\n<b>├ Выданных:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_week=True))}</code>'
#                             f'\n<b>└ Слетевших:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_week=True))}</code>'

#                             '\n\n<b>🗓 С начала месяца:</b>'
#                             f'\n<b>├ Выданных:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=17, buyed_at_month=True))}</code>'
#                             f'\n<b>└ Слетевших:</b> <code>{len(await select_phone_queues(group_id=group_info.group_id, status=18, slet_at_month=True))}</code>'
#                         )
#                     )