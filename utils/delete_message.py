
async def delete_message(bot, callback):
    try:
        await bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )
    except:
        try:
            await callback.answer(
                '🚫 Не удалось удалить сообщение!',
                show_alert=True
            )
        except:
            pass


async def delete_user_message(bot, message):
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    except:
        pass


async def delete_message_by_id(bot, chat_id, message_id):
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except:
        pass


async def delete_message_by_callback(bot, callback):
    try:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    except:
        pass

