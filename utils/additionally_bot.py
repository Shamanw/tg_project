import asyncio
import traceback

from aiogram.exceptions import TelegramRetryAfter


async def BotSendMessage(
    bot,
    chat_id = None,
    text = None,
    reply_markup = None,
    message_thread_id = None,
    parse_mode = 'HTML',
    entities = None,
    link_preview_options = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    allow_sending_without_reply = None,
    disable_web_page_preview = True,
    reply_to_message_id = None,
    request_timeout = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await bot.send_message(
                chat_id=chat_id,
                text=text,
                message_thread_id=message_thread_id,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id,
                request_timeout=request_timeout
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotSendMessage] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'chat not found' in str(e):
                print(f"[BotSendMessage] Chat not found")
            else:
                traceback.print_exc()
                print(f"[BotSendMessage] Error: {e}")
            return e
    return None


async def MessageReply(
    message,
    text = None,
    reply_markup = None,
    parse_mode = 'HTML',
    entities = None,
    link_preview_options = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    allow_sending_without_reply = None,
    disable_web_page_preview = True,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await message.reply(
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                disable_web_page_preview=disable_web_page_preview
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[MessageReply] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[MessageReply] Error: {e}")
            return e
    return None


async def MessageAnswer(
    message,
    text = None,
    reply_markup = None,
    parse_mode = 'HTML',
    entities = None,
    link_preview_options = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    allow_sending_without_reply = None,
    disable_web_page_preview = True,
    reply_to_message_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await message.answer(
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[MessageAnswer] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[MessageAnswer] Error: {e}")
            return e
    return None


async def MessageAnswerPhoto(
    message,
    photo,
    caption,
    parse_mode = 'HTML',
    caption_entities = None,
    has_spoiler = None,
    entities = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    reply_markup = None,
    allow_sending_without_reply = None,
    reply_to_message_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                has_spoiler=has_spoiler,
                entities=entities,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_to_message_id=reply_to_message_id
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[MessageAnswerPhoto] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[MessageAnswerPhoto] Error: {e}")
            return e
    return None


async def CallbackAnswer(
        callback,
        text = None,
        show_alert = None,
        url = None,
        cache_time = None,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await callback.answer(
                text=text,
                show_alert=show_alert,
                url=url,
                cache_time=cache_time
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[CallbackAnswer] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[CallbackAnswer] Error: {e}")
            return e
    return None


async def CallbackMessageAnswer(
    callback,
    text = None,
    reply_markup = None,
    parse_mode = 'HTML',
    entities = None,
    link_preview_options = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    allow_sending_without_reply = None,
    disable_web_page_preview = True,
    reply_to_message_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await callback.message.answer(
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[CallbackMessageAnswer] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[CallbackMessageAnswer] Error: {e}")
            return e

    return None


async def CallbackMessageReply(
    callback,
    text = None,
    parse_mode = 'HTML',
    entities = None,
    link_preview_options = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    reply_markup = None,
    allow_sending_without_reply = None,
    disable_web_page_preview = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await callback.message.reply(
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                disable_web_page_preview=disable_web_page_preview,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[CallbackMessageReply] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[CallbackMessageReply] Error: {e}")
            return e

    return None


async def BotEditText(
        bot,
        text = None,
        chat_id = None,
        message_id = None,
        inline_message_id = None,
        parse_mode = 'HTML',
        entities = None,
        link_preview_options = None,
        reply_markup = None,
        disable_web_page_preview = True,
        request_timeout = None,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview,
                request_timeout=request_timeout
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotEditText] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'message is not modified' in str(e):
                return e
            else:
                traceback.print_exc()
                print(f"[BotEditText] Error: {e}")
                return e
    return None


async def BotEditCaption(
        bot,
        chat_id = None,
        message_id = None,
        inline_message_id = None,
        caption = None,
        parse_mode = 'HTML',
        caption_entities = None,
        reply_markup = None,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                reply_markup=reply_markup
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotEditCaption] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'message is not modified' in str(e):
                return e
            else:
                traceback.print_exc()
                print(f"[BotEditCaption] Error: {e}")
                return e
    return None


async def MessageEditText(
        message,
        text = None,
        inline_message_id = None,
        parse_mode = 'HTML',
        entities = None,
        link_preview_options = None,
        reply_markup = None,
        disable_web_page_preview = True,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await message.edit_text(
                text=text,
                inline_message_id=inline_message_id,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[MessageEditText] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'message is not modified' in str(e):
                return e
            else:
                traceback.print_exc()
                print(f"[MessageEditText] Error: {e}")
                return e
    return None


async def CallbackEditText(
        callback,
        text = None,
        inline_message_id = None,
        parse_mode = 'HTML',
        entities = None,
        link_preview_options = None,
        reply_markup = None,
        disable_web_page_preview = True,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await callback.message.edit_text(
                text=text,
                inline_message_id=inline_message_id,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_web_page_preview
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[CallbackEditText] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'message is not modified' in str(e):
                await CallbackAnswer(callback=callback, text='✖️ Нет изменений', show_alert=False)
                return e
            else:
                traceback.print_exc()
                print(f"[CallbackEditText] Error: {e}")
                return e
    return None


async def CallbackEditCaption(
    callback,
    inline_message_id = None,
    caption = None,
    parse_mode = 'HTML',
    caption_entities = None,
    reply_markup = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await callback.message.edit_caption(
                inline_message_id=inline_message_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                reply_markup=reply_markup
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[CallbackEditCaption] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'message is not modified' in str(e):
                await CallbackAnswer(callback=callback, text='✖️ Нет изменений', show_alert=False)
                return e
            else:
                traceback.print_exc()
                print(f"[CallbackEditCaption] Error: {e}")
                return e
    return None


async def BotEditMessageReplyMarkup(
        bot,
        chat_id = None,
        message_id = None,
        inline_message_id = None,
        reply_markup = None,
        request_timeout = None,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
                reply_markup=reply_markup,
                request_timeout=request_timeout
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotEditMessageReplyMarkup] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[BotEditMessageReplyMarkup] Error: {e}")
            return e
    return None


async def BotSendPhoto(
    bot,
    chat_id = None,
    photo = None,
    message_thread_id = None,
    caption = None,
    parse_mode = 'HTML',
    caption_entities = None,
    has_spoiler = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    reply_markup = None,
    allow_sending_without_reply = None,
    reply_to_message_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                message_thread_id=message_thread_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                has_spoiler=has_spoiler,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_to_message_id=reply_to_message_id,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotSendPhoto] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'chat not found' in str(e):
                print(f"[BotSendPhoto] Chat not found")
            else:
                traceback.print_exc()
                print(f"[BotSendPhoto] Error: {e}")
            return False
    return None


async def BotSendDocument(
    bot,
    chat_id = None,
    document = None,
    message_thread_id = None,
    thumbnail = None,
    caption = None,
    parse_mode = 'HTML',
    caption_entities = None,
    disable_content_type_detection = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    reply_markup = None,
    allow_sending_without_reply = None,
    reply_to_message_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await bot.send_document(
                chat_id=chat_id,
                document=document,
                message_thread_id=message_thread_id,
                thumbnail=thumbnail,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                disable_content_type_detection=disable_content_type_detection,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_to_message_id=reply_to_message_id,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotSendDocument] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'chat not found' in str(e):
                print(f"[BotSendDocument] Chat not found")
            else:
                traceback.print_exc()
                print(f"[BotSendDocument] Error: {e}")
            return False
    return None


async def BotDeleteMessage(
        bot,
        chat_id = None,
        message_id = None,
        request_timeout = None,
        max_retries = 5,
        default_retry_after = 5
    ):
    for attempt in range(max_retries):
        try:
            response = await bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
                request_timeout=request_timeout
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotDeleteMessage] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[BotDeleteMessage] Error: {e}")
            return e
    return None


async def MessageAnswerPhoto(
    message,
    photo,
    caption,
    parse_mode = 'HTML',
    caption_entities = None,
    has_spoiler = None,
    entities = None,
    disable_notification = None,
    protect_content = None,
    reply_parameters = None,
    reply_markup = None,
    allow_sending_without_reply = None,
    reply_to_message_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                has_spoiler=has_spoiler,
                entities=entities,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_to_message_id=reply_to_message_id
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[MessageAnswerPhoto] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[MessageAnswerPhoto] Error: {e}")
            return e
    return None


async def BotGetChatMember(
    bot,
    chat_id = None,
    user_id = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotGetChatMember] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            if 'PARTICIPANT_ID_INVALID' in str(e):
                pass
            else:
                traceback.print_exc()
                print(f"[BotGetChatMember] Error: {e}")
            return e
    return None


async def BotBanChatMember(
    bot,
    chat_id = None,
    user_id = None,
    until_date = None,
    revoke_messages = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await bot.ban_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
            revoke_messages=revoke_messages,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotBanChatMember] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[BotBanChatMember] Error: {e}")
            return e
    return None


async def BotUnBanChatMember(
    bot,
    chat_id = None,
    user_id = None,
    only_if_banned = None,
    max_retries = 5,
    default_retry_after = 5
):
    for attempt in range(max_retries):
        try:
            response = await bot.unban_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            only_if_banned=only_if_banned,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotUnBanChatMember] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[BotUnBanChatMember] Error: {e}")
            return e
    return None


async def BotCopyMessage(
        bot,
        chat_id = None,
        from_chat_id = None,
        message_id = None,
        message_thread_id = None,
        caption = None,
        parse_mode = 'HTML',
        caption_entities = None,
        disable_notification = None,
        protect_content = None,
        reply_parameters = None,
        reply_markup = None,
        allow_sending_without_reply = True,
        reply_to_message_id = None,
        request_timeout = None,
        max_retries = 10,
        default_retry_after = 10
    ):
    for attempt in range(max_retries):
        try:
            response = await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                message_thread_id=message_thread_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_to_message_id=reply_to_message_id,
                request_timeout=request_timeout,
            )
            return response
        except TelegramRetryAfter as e:
            wait_time = e.retry_after or default_retry_after
            print(f"[BotCopyMessage] Rate limit exceeded. Retrying after {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            traceback.print_exc()
            print(f"[BotCopyMessage] Error: {e}")
            return None
    return None