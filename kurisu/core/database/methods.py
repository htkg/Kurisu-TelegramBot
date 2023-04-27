from datetime import datetime
from kurisu.core.database.schema import Chat, Messages
from loguru import logger
from peewee import IntegrityError


def init_chat(id, type, **kwargs):
    try:
        chat, created = Chat.get_or_create(id=id, type=type, defaults=kwargs)

        if not created:
            chat.update(**kwargs).execute()

    except IntegrityError as e:
        logger.debug(f"IntegrityError: {str(e)}")
        chat = Chat.get(Chat.id == id)
        created = False

        chat.update(**kwargs).execute()

    return chat, created


def create_group(id, type, **kwargs):
    group, created = init_chat(id, type, **kwargs)
    if created:
        logger.success(f"New chat: {kwargs['title']} ({id}) ({type})")
    return group, created


def create_user(id, **kwargs):
    user, created = init_chat(id, type="ChatType.PRIVATE", **kwargs)
    if created:
        logger.success(f"New user: {kwargs['username']} ({id})")
    return user, created


def create_message(user, **kwargs):
    message, created = Messages.get_or_create(from_user=user, **kwargs)
    if created:
        logger.success(f"New message: {kwargs['content']} ({kwargs['id']})")
    return message, created
