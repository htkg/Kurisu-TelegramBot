from datetime import datetime
from kurisu.core.database.schema import Chat, Messages, Plugins, PluginSettings
from loguru import logger
from peewee import IntegrityError

def init_chat_or_update(id, type, **kwargs):
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
    group, created = init_chat_or_update(id, type, **kwargs)
    if created:
        logger.success(f"New chat: {kwargs['title']} ({id}) ({type})")
    return group, created

def create_user(id, **kwargs):
    user, created = init_chat_or_update(id, type="ChatType.PRIVATE", **kwargs)
    if created:
        logger.success(f"New user: {kwargs['username']} ({id})")
    return user, created

def create_message(user, **kwargs):
    message, created = Messages.get_or_create(from_user=user, **kwargs)
    if created:
        logger.success(f"New message: {kwargs['content']} ({kwargs['id']})")
    return message, created

def create_or_update_plugin(**kwargs):
    try:
        plugin, created = Plugins.get_or_create(**kwargs)
        logger.success(f"Plugin initialized {kwargs['name']} ({kwargs['version']})")

        if not created:
            plugin.update(**kwargs).execute()

    except IntegrityError as e:
        logger.success(f"Plugin already initialized {kwargs['name']} ({kwargs['version']})")
        plugin = Plugins.get(Plugins.name == kwargs['name'])
        created = False

        plugin.update(**kwargs).execute()

    return plugin, created

def get_plugins(name=False):
    if name:
        return Plugins.select().where(Plugins.name == name)
    else:
        return Plugins.select()

def create_or_update_plugin_settings(plugin, chat, **kwargs):
    try:
        settings, created = PluginSettings.get_or_create(
            plugin=plugin,
            chat=chat,
            defaults=kwargs
        )

        if not created:
            settings.update(**kwargs).execute()

    except IntegrityError as e:
        logger.debug(f"IntegrityError: {str(e)}")
        settings = PluginSettings.get(
            PluginSettings.plugin == plugin,
            PluginSettings.chat == chat
        )
        created = False

        settings.update(**kwargs).execute()

    return settings, created