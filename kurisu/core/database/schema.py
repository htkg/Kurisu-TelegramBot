from dotenv import dotenv_values
from datetime import datetime
from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase

config = dotenv_values("db.env")

db = PostgresqlExtDatabase(
    config["db_name"],
    user=config["db_user"],
    password=config["db_pass"],
    host=config["db_host"],
    port=config["db_port"],
)


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
    permission = ForeignKeyField(
        Permission, backref="users", on_delete="CASCADE")
    value = BooleanField(default=False)

    class Meta:
        indexes = ((("chat", "permission"), True),)


class Messages(BaseModel):
    id = BigIntegerField()
    from_chat = ForeignKeyField(
        Chat, backref="messages", null=True, default=None)
    date = DateTimeField()
    content = TextField(null=True)
    from_user = ForeignKeyField(
        Chat, backref="messages", lazy_load=True, on_delete="CASCADE"
    )
    is_command = BooleanField()
    reply_to_msg_id = IntegerField(null=True)

    class Meta:
        primary_key = CompositeKey("id", "from_chat")


def initialize_tables():
    with db:
        db.create_tables([Chat, Permission, ChatPermissions, Messages])


def prune_db():
    with db:
        db.drop_tables(
            [Chat, Permission, ChatPermissions, Messages], cascade=True)