import traceback
from aiogram import Router, F
from aiogram.types import Message
from utils.additionally_bot import BotDeleteMessage

clear_notify_router = Router()

@clear_notify_router.message(lambda message: hasattr(message, 'boost_added') and message.boost_added)
async def handle_boost_added(message: Message, bot):
    try:
        chat_id = message.chat.id
        message_id = message.message_id
        # boost_count = message.boost_added.get('boost_count', 0)
        await BotDeleteMessage(bot, chat_id=chat_id, message_id=message_id)
    except Exception as e:
        traceback.print_exc()
        print(f"Ошибка при обработке сообщения о бусте: {e} | message: {message}")


@clear_notify_router.message(F.content_type.in_(
    ["new_chat_members", "left_chat_member", 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
     'group_chat_created', 'supergroup_chat_created', 'channel_chat_created']))
async def message_handler(message: Message, bot):
    try:
        await BotDeleteMessage(bot, chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        traceback.print_exc()
        print(f"Ошибка при обработке системного уведомления: {e} | message: {message}")



# @clear_notify_router.message()
# async def message_handler(message: Message, bot):
#     print(f'\n\n\nMESSAGE: {message}')

# @clear_notify_router.message(F.content_type.in_(
#     ["new_chat_members", "left_chat_member", 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
#      'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'message_auto_delete_timer_changed',
#      'migrate_to_chat_id', 'pinned_message', 'invoice', 'successful_payment', 'connected_website', 'passport_data',
#      'proximity_alert_triggered', 'voice_chat_scheduled', 'voice_chat_started', 'voice_chat_ended',
#      'voice_chat_participants_invited', 'web_app_data', 'video_chat_scheduled', 'video_chat_started',
#      'video_chat_ended', 'video_chat_participants_invited']))
