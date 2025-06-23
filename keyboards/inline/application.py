from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_application_kb(application_id, ban_text='🚫 Забанить', ban_callback='BAN'):
    application_id = str(application_id)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Одобрить',
                    callback_data='APPL|YES|' + application_id
                ),
                InlineKeyboardButton(
                    text='❌ Отклонить',
                    callback_data='APPL|NO|' + application_id
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f'{ban_text} пользователя',
                    callback_data=f'APPL|{ban_callback}|' + application_id + '|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'{ban_text} пользователя (без уведомления)',
                    callback_data=f'APPL|{ban_callback}|' + application_id + '|1'
                )
            ]
        ]
    )
    return markup

def admin_application_ban_kb(application_id, ban_text='🚫 Забанить', ban_callback='BAN'):
    application_id = str(application_id)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'{ban_text} пользователя',
                    callback_data=f'APPL|{ban_callback}|' + application_id + '|0'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'{ban_text} пользователя (без уведомления)',
                    callback_data=f'APPL|{ban_callback}|' + application_id + '|1'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Закрыть',
                    callback_data='DELETE'
                )
            ]

        ]
    )
    return markup
