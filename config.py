BOT_TOKEN = '7718920119:AAFMy1sjWYfkHsfeSrcKjht_lfTanPGbi7E'
SECOND_BOT_TOKEN = '7659884337:AAGixlHgFhYwSXEse6lmpWcMFDqFnGscpgg'
ADMIN_ID = 7858719360

from pyrogram import Client

phone_number_main = '380661766553'
pyro_client = Client(
    name=f'sessions/{phone_number_main}',
    phone_number=phone_number_main,
    password='Born2Kill',
    api_id=28490224,
    api_hash='bee5dc311850ca1b27a27603a29ff45d',
    device_model='iPhone XS',
    system_version='16.6.1',
    app_version='Telegram iOS (27585)',
    lang_code='en',
)

phone_number_second = '380509102754'
pyro_client_second = Client(
    name=f'sessions/{phone_number_second}',
    phone_number=phone_number_second,
    password='Lavanda1488!',
    api_id=28490224,
    api_hash='bee5dc311850ca1b27a27603a29ff45d',
    device_model='iPhone XS',
    system_version='16.6.1',
    app_version='Telegram iOS (27585)',
    lang_code='en',
)



