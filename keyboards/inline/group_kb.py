import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.commands.main import *
from database.commands.groups import *

from utils.misc import decline_day, famount, get_time_at_period


async def group_menu_kb(group_id):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔄 Обновить',
                    callback_data=f'gcn|u|{group_id}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔗 Привязать свой баланс к группе',
                    callback_data=f'gcn|a|{group_id}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='❎ Отвязать свой баланс от группы',
                    callback_data=f'gcn|d|{group_id}'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='👥 Пользователи привязавшие баланс',
                    callback_data=f'gcn|i|{group_id}'
                ),
            ],
        ]
    )
    return markup


async def catalog_choose_kb():
    buttons = []
    total = 0
    otrabotka = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
    if otrabotka:
        total += otrabotka
        buttons.append([
            InlineKeyboardButton(
                text=f'Отработанные: {otrabotka} шт.',
                callback_data='CATALOG|MENU|333'
            )
        ])
    sletevshie = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
    if sletevshie:
        total += sletevshie
        buttons.append([
            InlineKeyboardButton(
                text=f'Отработанные с отлегой: {sletevshie} шт.',
                callback_data='CATALOG|MENU|222'
            )
        ])
    bez_otlegi = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
    if bez_otlegi:
        total += bez_otlegi
        buttons.append([
            InlineKeyboardButton(
                text=f'Без отлеги: {bez_otlegi} шт.',
                callback_data='CATALOG|MENU|111|1'
            )
        ])
    qwrites = await select_many_records(OtlegaGroup)
    if qwrites:
        qwrites = qwrites[:95]
        for qwrite in qwrites:
            accs_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=qwrite.unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)
            if accs_count:
                total += accs_count
                buttons.append([
                    InlineKeyboardButton(
                        text=f'Отлега {qwrite.count_days} {await decline_day(int(qwrite.count_days))}: {accs_count} шт.',
                        callback_data=f'CATALOG|MENU|{qwrite.unique_id}|1'
                    )
                ])
        buttons.append([
            InlineKeyboardButton(
                text='❌ Убрать лот по умолчанию',
                callback_data=f'CATALOG|LOT_CLEAR'
            ),
        ])
    if not total:
        buttons.append([
            InlineKeyboardButton(
                text='Нет доступных аккаунтов',
                callback_data='X'
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text=f'Закрыть',
            callback_data=f'DELETE'
        ),
        InlineKeyboardButton(
            text=f'Обновить',
            callback_data=f'CATALOG|M'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def catalog_menu_kb(unique_id, qwrite):
    buttons = []
    if unique_id == 111:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id_is_none=True, status=12, buyed_amount_is_not_none=True)
    elif unique_id == 222:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status=9, buyed_amount_is_not_none=True)
    elif unique_id == 333:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, tdata_status=0, status=18, alive_status_in=[2,3], buyed_amount_is_not_none=True)
    else:
        writes_count = await select_many_records(PhoneQueue, count=True, client_bot=1, otlega_unique_id=unique_id, status=12, set_at_more=int(qwrite.count_days), buyed_amount_is_not_none=True)

    if writes_count:
        buttons.append([
            InlineKeyboardButton(
                text='🔢 Купить tdata/session',
                callback_data=f'CATALOG|COUNT|M|{unique_id}'
            ),
        ])
        buttons.append([
            InlineKeyboardButton(
                text='🔑 Войти по СМС',
                callback_data=f'CATALOG|SMS|GET|{unique_id}'
            ),
        ])
        buttons.append([
            InlineKeyboardButton(
                text='📌 Установить как лот по умолчанию',
                callback_data=f'CATALOG|LOT_SET|{unique_id}'
            ),
        ])

    buttons.append([
        InlineKeyboardButton(
            text=f'‹ Назад',
            callback_data='CATALOG|M'
        ),
        InlineKeyboardButton(
            text=f'Обновить',
            callback_data=f'CATALOG|MENU|{unique_id}'
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
