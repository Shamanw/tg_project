from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def multi_kb(callback_data: str = 'START', text: str = '‹ Назад'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            ]
        ]
    )
    return markup


def multi_2_kb(callback_data: str = 'START', text: str = '🔄 Обновить', callback_data_back: str = 'START', text_back: str = '‹ Назад'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            ],
            [
                InlineKeyboardButton(
                    text=text_back,
                    callback_data=callback_data_back
                )
            ]
        ]
    )
    return markup



def phone_write_manage_kb(primary_id, status=None):
    buttons = []
    
    buttons.append(
        [
            InlineKeyboardButton(
                text='🗂 TDATA',
                callback_data=f'PHONE|TDATA|{primary_id}'
            ),
            InlineKeyboardButton(
                text='🗄 SESSION',
                callback_data=f'PHONE|SESSION|{primary_id}'
            )
        ],
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text='🗄⬆️ Выгрузить в клиентский бот',
                callback_data=f'PHONE|UNLOAD|{primary_id}'
            ),
        ],
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text='🗄⬇️ Забрать из клиентского бота',
                callback_data=f'PHONE|TAKE|{primary_id}'
            ),
        ],
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text='✅',
                callback_data=f'PHONE|SC|{primary_id}'
            ),
            InlineKeyboardButton(
                text='💵',
                callback_data=f'PHONE|PY|{primary_id}'
            ),
            InlineKeyboardButton(
                text='💢',
                callback_data=f'PHONE|SL|{primary_id}'
            ),
        ],
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text='🗑',
                callback_data=f'PHONE|D1|{primary_id}'
            ),
            InlineKeyboardButton(
                text='🗑 📉',
                callback_data=f'PHONE|D2|{primary_id}'
            ),
            InlineKeyboardButton(
                text='☠️',
                callback_data=f'PHONE|NV1|{primary_id}'
            ),
            InlineKeyboardButton(
                text='☠️ 📉',
                callback_data=f'PHONE|NV2|{primary_id}'
            ),
        ],
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text='🔄',
                callback_data=f'PHONE|U|{primary_id}'
            ),
            InlineKeyboardButton(
                text='❌',
                callback_data='DELETE'
            )
        ],
    )

    markup = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    return markup


def withdraw_kb(primary_id, status=None):
    buttons = [
        [
            InlineKeyboardButton(
                text='🔄 Обновить',
                callback_data=f'AWD|W|U|{primary_id}'
            )
        ],
        [
            InlineKeyboardButton(
                text='❌ Закрыть',
                callback_data='DELETE'
            )
        ],
    ]
    if status is not None and status == 0:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='❌ Отменить с возвратом',
                    callback_data=f'AWD|W|CL|{primary_id}'
                )
            ],
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text='🗑 Удалить без возврата',
                    callback_data=f'AWD|W|DD|{primary_id}'
                )
            ],
        )
    
    markup = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    return markup


def subscribe_kb(channel_link):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Подписаться',
                    url=channel_link
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌',
                    callback_data='DELETE'
                )
            ]
        ]
    )
    return markup


def manual_check_kb(manual_link):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='👁 Прочитать',
                    url=manual_link
                )
            ],
            [
                InlineKeyboardButton(
                    text='➡️ Продолжить',
                    callback_data='DROP_WORK|MANUAL'
                )
            ]
        ]
    )
    return markup


async def multi_new_kb(text: str = '‹ Назад', callback_data: str = 'START'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            ],
        ]
    )
    return markup

async def multi_new_2_kb(text: str = '‹ Назад', callback_data: str = 'START', text2: str = '‹‹ В главное меню', callback_data2: str = 'START'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            ],
            [
                InlineKeyboardButton(
                    text=text2,
                    callback_data=callback_data2
                )
            ]
        ]
    )
    return markup

async def multi_new_2_2_kb(text: str = '‹ Назад', callback_data: str = 'START', text2: str = '‹‹ В главное меню', callback_data2: str = 'START'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                ),
                InlineKeyboardButton(
                    text=text2,
                    callback_data=callback_data2
                )
            ]
        ]
    )
    return markup

async def multi_new_3_kb(text: str = '‹ Назад', callback_data: str = 'START', text2: str = '‹‹ В главное меню', callback_data2: str = 'START', text3: str = '‹‹ В главное меню', callback_data3: str = 'START'):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            ],
            [
                InlineKeyboardButton(
                    text=text2,
                    callback_data=callback_data2
                )
            ],
            [
                InlineKeyboardButton(
                    text=text3,
                    callback_data=callback_data3
                )
            ]
        ]
    )
    return markup


async def delete_kb():
    markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✖️ Закрыть',
                    callback_data='DELETE'
                )
            ]
        ]
    )
    return markup