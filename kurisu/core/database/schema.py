from kurisu import db_cfg
from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField
from loguru import logger

db = PostgresqlExtDatabase(**db_cfg)


class BaseModel(Model):
    class Meta:
        database = db


class Chat(BaseModel):
    id = BigIntegerField(primary_key=True)
    username = CharField(max_length=32, null=True)
    title = CharField(max_length=256, null=True)
    type = CharField(max_length=32)
    first_name = CharField(max_length=64, null=True)
    last_name = CharField(max_length=64, null=True)
    language_code = CharField(max_length=10, null=True)


class Permission(BaseModel):
    permission_name = CharField(max_length=100, unique=True)
    description = TextField(null=True)


class ChatPermissions(BaseModel):
    chat = ForeignKeyField(Chat, backref="permissions", on_delete="CASCADE")
    permission = ForeignKeyField(Permission, backref="users", on_delete="CASCADE")
    value = BooleanField(default=False)

    class Meta:
        indexes = ((("chat", "permission"), True),)


class Messages(BaseModel):
    id = BigIntegerField()
    from_chat = ForeignKeyField(Chat, backref="messages")
    date = DateTimeField()
    content = TextField(null=True)
    from_user = ForeignKeyField(
        Chat, backref="messages", lazy_load=True, on_delete="CASCADE"
    )
    is_command = BooleanField()
    reply_to_msg_id = IntegerField(null=True)

    class Meta:
        primary_key = CompositeKey("id", "from_chat")

class Plugins(BaseModel):
    name = CharField(primary_key=True, max_length=100)
    description = TextField(null=True)
    version = CharField(max_length=10)

class PluginSettings(BaseModel):
    id = AutoField()
    plugin = ForeignKeyField(Plugins, backref="settings")
    chat = ForeignKeyField(Chat, backref="settings")
    settings = JSONField(null=True)
    enabled = BooleanField(default=True)
    
    class Meta:
        indexes = ((("plugin", "chat"), True),)
        
class RunPodTasks(BaseModel):
    task_guid = CharField(max_length=256, primary_key=True)
    date = DateTimeField()
    chat = ForeignKeyField(Chat, backref="tasks")
    user_id = BigIntegerField()
    message_id = BigIntegerField()
    status = CharField(max_length=60)
    parameters = JSONField(null=True)
    infotext = CharField(null=True)

def initialize_tables():
    with db:
        db.create_tables([Chat, Permission, ChatPermissions, Messages, Plugins, PluginSettings, RunPodTasks])
        logger.success("Database tables initialized")


def prune_db():
    with db:
        db.drop_tables([Chat, Permission, ChatPermissions, Messages, Plugins, PluginSettings, RunPodTasks])

# # Alter the table and add the new column
# with db:
#     db.create_tables([RunPodTasks])
#     db.execute_sql('ALTER TABLE RunPodTasks ADD COLUMN infotext TEXT')