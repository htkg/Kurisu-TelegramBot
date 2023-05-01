from pyrogram.types import InputMediaPhoto
import io
import base64
from PIL import Image
import json
from loguru import logger
from kurisu.core.database.methods import get_task
from pyrogram.errors.exceptions.flood_420 import FloodWait
import time
import asyncio

async def get_image_size(orientation):
    if orientation == "portrait":
        return 512, 768
    elif orientation == "landscape":
        return 768, 512
    else:
        return 512, 512


def update_task_db(task_db, results):
    task_db.status = results["status"]
    try:
        task_db.parameters = results["output"]["parameters"]
        task_db.infotext = results["output"]["infotext"]
    except:
        pass
    task_db.save()

async def send_images(client, chat_id, message_id, images):
    try:
        images_msg = await client.send_media_group(
            chat_id=chat_id, reply_to_message_id=message_id, media=images
        )
    except FloodWait:
        await asyncio.sleep(30)
        images_msg = await client.send_media_group(
            chat_id=chat_id, reply_to_message_id=message_id, media=images
        )
    return images_msg

def load_available_options():
    with open('kurisu/cogs/dream/data/options.json') as f:
        available_options = json.load(f)
    return available_options

def process_response_raw(res):
    imgs = []
    for i, i_b64 in enumerate(res['images']):
        image = Image.open(io.BytesIO(
            base64.b64decode(i_b64.split(",", 1)[0])))
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        imgs.append(InputMediaPhoto(buf))

    return imgs

async def update_in_progress_message(notification_msg, task_id, iteration):
    try:
        await notification_msg.edit_text(
            f"Job № `{task_id}` is in progress...\n\nHeartbeat: `{iteration}` (if heartbeat stops, then task suddenly died.)"
        )
    except Exception as e:
        pass


async def handle_completed_task(client, results, task_id, notification_msg, start_time):
    images = process_response_raw(results['output'])
    execution_time = int(results['executionTime']) / 1000
    cost = 0.0002 * (execution_time + 30)

    output_params = results['output']['parameters']
    enable_hr = output_params['enable_hr']
    hr_scale = output_params['hr_scale'] if enable_hr else 1
    width = round(output_params['width'] * hr_scale)
    height = round(output_params['height'] * hr_scale)

    msg = format_completed_message(results, width, height, start_time, execution_time, cost)
    images[0].caption = msg

    logger.success(f"Job № `{task_id}` done in {execution_time} seconds.")
    await send_images_and_update_caption(client, task_id, notification_msg, images, msg)


async def send_images_and_update_caption(client, task_id, notification_msg, images, msg):
    task_db = get_task(task_guid=task_id)
    
    try:
        images_msg = await client.send_media_group(chat_id=task_db.chat_id, reply_to_message_id=task_db.message_id, media=images)
    except FloodWait:
        await asyncio.sleep(30)
        images_msg = await client.send_media_group(chat_id=task_db.chat_id, reply_to_message_id=task_db.message_id, media=images)

    old_msg_time = notification_msg.date
    images_msg_time = images_msg[0].date
    time_delta = round((images_msg_time - old_msg_time).total_seconds(), 2)

    msg += f"<i> | Actual: {time_delta}s</i>"
    await images_msg[0].edit_caption(caption=msg)
    await notification_msg.delete()


def format_completed_message(results, width, height, start_time, execution_time, cost):
    info_text = json.loads(results['output']['info'])
    msg = f"**Job № `{results['id']}`**\n═══"

    for parameter in info_text:
        txt_parameter = info_text[parameter]
        if txt_parameter and not parameter in ['prompt', 'negative_prompt', 'all_prompts', 'all_negative_prompts','infotexts', 'width', 'height', 'sd_model_hash', 'seed_resize_from_w', 'seed_resize_from_h']:
            if type(txt_parameter) == list:
                txt_parameter = "`, `".join([str(item) for item in txt_parameter])

            msg += f"\n**{parameter.replace('_', ' ').title()}**: `{txt_parameter}`"

    code_exc_time = round(time.time() - start_time, 2)
    msg += f"\n**Width**: `{width}`\n**Height**: `{height}`\n═══\n<i>Cost: {round(cost, 4)}$ | Inference: {execution_time}s | Code: {code_exc_time}s</i>"

    return msg