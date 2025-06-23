from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='📊 Статистика',
                    callback_data='STAT|M'
                ),
                InlineKeyboardButton(
                    text='📁 Архив',
                    callback_data='ARCHIVE|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Управление',
                    callback_data='MNG|M'
                ),
                InlineKeyboardButton(
                    text='🌐 Прокси',
                    callback_data='PROXY|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🤖 Автовывод',
                    callback_data='AWD|M'
                ),
                InlineKeyboardButton(
                    text='🔂 Исключения',
                    callback_data='EXC|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='*️⃣ Настройки',
                    callback_data='STNGS|M'
                ),
                InlineKeyboardButton(
                    text='🔍 Поиск номера',
                    callback_data='PHONE|S'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='💢 Ожидание слёта',
                    callback_data='CRS|M'
                ),
                InlineKeyboardButton(
                    text='♿️ Неактивные',
                    callback_data='INACTIVE|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🕒 Отлега',
                    callback_data='OTLEGA|M'
                ),
                InlineKeyboardButton(
                    text='🗂 Загрузить TDATA',
                    callback_data='TDATA|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔁🌐 Прокси для конвертера',
                    callback_data='CONVPROXY|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='✉️ Рассылка',
                    callback_data='send|m'
                ),
            ],
        ]
    )
    return markup


def drop_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='📱 Добавить номера',
                    callback_data='DROP_WORK|ADD_PHONES'
                )
            ],
            [
                InlineKeyboardButton(
                    text='📊 Статистика',
                    callback_data='DROP_WORK|STAT'
                ),
                InlineKeyboardButton(
                    text='💳 Вывод',
                    callback_data='DROP_WORK|W|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⏳ Очередь на авторизацию',
                    callback_data='DROP_WORK|PHONES|M|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='☠️ Слетевшие аккаунты',
                    callback_data='SLET|M'
                )
            ],
        ]
    )
    return markup


def client_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='⬆️ Подать заявку на доступ к функционалу',
                    callback_data='SUBMIT_APPLICATION'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='✉️ Мои заявки',
                    callback_data='MY_APPLICATIONS'
                )
            ]
        ]
    )
    return markup


async def clients_menu_kb():
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🛒 Товары',
                    callback_data='CATALOG|M'
                ),
            # ],
            # [
                InlineKeyboardButton(
                    text='🔁 Конвертер',
                    callback_data='CONVERT|M'
                ),
            ],
            [
                InlineKeyboardButton(
                    text='👤 Профиль',
                    callback_data='PROFILE|M'
                ),
                InlineKeyboardButton(
                    text='🤝 Партнёрам',
                    callback_data='PARTNERS|M'
                )
            ],
            [
                InlineKeyboardButton(
                    text='📌 Инструкция',
                    callback_data='RULES'
                ),
                InlineKeyboardButton(
                    text='🆘 Поддержка',
                    callback_data='SUPPORT'
                )
            ],
        ]
    )
    return markup

 





