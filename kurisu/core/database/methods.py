from datetime import datetime
from kurisu.core.database.schema import Chat, Messages, Plugins, PluginSettings, RunPodTasks
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
        logger.success(
            f"Plugin already initialized {kwargs['name']} ({kwargs['version']})"
        )
        plugin = Plugins.get(Plugins.name == kwargs["name"])
        created = False

    return plugin, created



def get_plugins(name=False):
    if name:
        return Plugins.select().where(Plugins.name == name)
    else:
        return Plugins.select()


def create_or_update_plugin_settings(plugin, chat, params=None):
    settings, created = PluginSettings.get_or_create(
        plugin=plugin, chat=chat, defaults={"settings": params}
    )
    
    if not created:
        settings.update(settings=params).execute()
        
    return settings, created

def delete_plugin_settings(plugin, chat):
    settings = PluginSettings.get(plugin=plugin, chat=chat)
    settings.delete_instance()


def get_plugin_settings(plugin, chat):
    try:
        settings = PluginSettings.get(plugin=plugin, chat=chat)
        return settings
    except PluginSettings.DoesNotExist:
        return None

def create_or_update_task(**kwargs):
    try:
        task, created = RunPodTasks.get_or_create(**kwargs)
        if created:
            logger.success(f"New task: {kwargs['task_guid']}")
        
        if not created:
            task.update(**kwargs).execute()
    except IntegrityError as e:
        logger.success(f"Task already initialized {kwargs['task_guid']}")
        task = RunPodTasks.get(RunPodTasks.task_guid == kwargs["task_guid"])
        created = False
    
    return task, created

def get_task(task_guid):
    try:
        task = RunPodTasks.get(task_guid=task_guid)
        return task
    except RunPodTasks.DoesNotExist:
        return None

def get_tasks(chat):
    try:
        tasks = RunPodTasks.select().where(RunPodTasks.chat == chat)
        return tasks
    except RunPodTasks.DoesNotExist:
        return None
