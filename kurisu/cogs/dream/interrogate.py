from pyrogram import Client, filters
from PIL import Image
from io import BytesIO
import base64
from kurisu.cogs.dream.runpod_reqs import sync_run
from loguru import logger
from kurisu.core.database.methods import create_or_update_task, get_task
import random
from datetime import datetime


def pil_to_base64(pil_image):
    with BytesIO() as stream:
        pil_image.save(stream, "PNG", pnginfo=None)
        base64_str = str(base64.b64encode(stream.getvalue()), "utf-8")
        return "data:image/png;base64," + base64_str

@Client.on_message(filters.command(["clip", "booru"], prefixes="/") & ~(filters.reply | filters.photo), group=2)
async def describe_error(client, message):
    await message.reply("Отправьте фото или ответьте на сообщение где есть фото", quote=True)

@Client.on_message(filters.command(["clip", "booru"], prefixes="/") & (filters.reply | filters.photo), group=2)
async def describe(client, message):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    chat_id = message.chat.id
    message_id = message.id
    command = message.command[0]
    
    if command == "clip":
        mode = "clip"
    elif command == "booru":
        mode = "deepdanbooru"
        
    if message.reply_to_message:
        to_download_media = message.reply_to_message
    else:
        to_download_media = message

    fp = await client.download_media(to_download_media)
    image = Image.open(fp)
    image = pil_to_base64(image)
    payload = {"input": {"interrogate": {"image": image, "model": mode}}}
    
    logger.info(f"User {message.from_user.id} requesting {mode}...")
    status = "IN_QUEUE"
    random_guid = f"{mode}-{random.randint(1, 99999999)}"
    create_or_update_task(task_guid=random_guid, date=datetime.now(), status=status, user_id=user_id, chat_id=chat_id, message_id=message_id)
    res = await sync_run(payload)
    caption = res['output']['caption'].replace("_", " ")
    task_db = get_task(task_guid=random_guid)
    task_db.status = res['status']
    task_db.parameters = mode
    task_db.infotext = caption
    task_db.save()
    
    await message.reply(f"`{caption}`", quote=True)