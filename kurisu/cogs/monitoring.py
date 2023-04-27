from kurisu.core.database.methods import *
from pyrogram import Client, filters
from pyrogram.enums.message_entity_type import MessageEntityType
from pyrogram.enums.chat_type import ChatType
from loguru import logger
from pyrogram.types import User

@Client.on_message(filters.text | filters.photo | filters.media, group=0)
async def log_event(client, update):
    chatid = update.chat.id
    user = update.from_user or update.sender_chat
    userid = user.id or chatid
    chat_type = update.chat.type
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    fullname = f"{first_name or ''} {last_name or ''}".strip()
    language_code = user.language_code if isinstance(user, User) and user.language_code else None
    title = update.chat.title or fullname
    message = update.text or update.caption
    message_reply = update.reply_to_message.id if update.reply_to_message else None

    db_user, _ = create_user(userid, username=username, first_name=first_name, last_name=last_name, language_code=language_code)

    if chat_type != ChatType.PRIVATE:
        chat_username = update.chat.username
        create_group(chatid, username=chat_username, title=title, type=chat_type)

    is_command = update.entities is not None and update.entities[0].type == MessageEntityType.BOT_COMMAND

    create_message(db_user, id=update.id, from_chat=chatid, date=update.date, content=message, is_command=is_command, reply_to_msg_id=message_reply)