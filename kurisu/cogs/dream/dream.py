import json
import asyncio
import time
from pyrogram import Client, filters
from kurisu.core.database.methods import (
    create_or_update_plugin_settings,
    get_plugin_settings,
    get_task,
    delete_plugin_settings,
)
from kurisu.cogs.dream.requests import async_run, check_status
from kurisu.cogs.dream.settings import get_params
from loguru import logger
from kurisu.cogs.dream.helpers import update_task_db, update_in_progress_message, handle_completed_task, get_image_size

with open("kurisu/cogs/dream/data/default_params.json", "r") as f:
    params = json.load(f)


async def refresh_task_status(client, task_id, notification_msg):
    start_time = time.time()
    prev_status = None
    iteration = 0

    while True:
        results = await check_status(task_id)

        if results["status"] != prev_status:
            update_task_db(get_task(task_guid=task_id), results)
            prev_status = results["status"]

        if results["status"] == "IN_PROGRESS":
            iteration += 1
            await update_in_progress_message(notification_msg, task_id, iteration)

        elif results["status"] == "COMPLETED":
            await handle_completed_task(client, results, task_id, notification_msg, start_time)
            break

        elif results["status"] == "FAILED":
            logger.error(f"Job № `{task_id}` failed.")
            await notification_msg.edit_text(f"Job № `{task_id}` failed.")
            break

        await asyncio.sleep(4)

@Client.on_message(filters.command(["dream"], prefixes="/") & ~ filters.reply & ~ filters.photo, group=2)
async def txt2img(client, message):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    
    pluginsettings = get_plugin_settings(plugin='txt2img', chat=user_id)
    
    if not pluginsettings:
        create_or_update_plugin_settings(plugin='txt2img', chat=user_id, params=params)
        pluginsettings = get_plugin_settings(plugin='txt2img', chat=user_id)

    sd_config = pluginsettings.settings

    kb = await get_params(sd_config)
    prompt = " ".join(message.command[1:]).strip()

    if not prompt:
        await message.reply_text("You need to provide prompt. By default, default settings in place. If you want to change settings, please use buttons below.", reply_markup=kb, reply_to_message_id=message.id)
        return

    width, height = await get_image_size(sd_config['orientation'])

    generation_options = {
        "prompt": f"masterpiece, best quality, {prompt}",
        "negative_prompt": sd_config['negative_prompt'],
        "enable_hr": sd_config['upscale'],
        "denoising_strength": float(sd_config['denoising_strength']),
        "cfg_scale": float(sd_config['cfg_scale']),
        "steps": int(sd_config['steps']),
        "batch_size": int(sd_config['batch_size']),
        "sampler_index": sd_config['sampler'],
        "sampler_name": sd_config['sampler'],
        "width": int(width),
        "height": int(height),
        "hr_upscaler": sd_config['hr_upscaler'],
        "hr_scale": float(sd_config['hr_scale']),
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
        }
    }
    payload = {"input": {"txt2img": generation_options}}

    task_id = await async_run(payload=payload, user_id=user_id, chat_id=message.chat.id, message_id=message.id,debug="de27d103-41b8-440f-b0b5-9cd936bbafec")

    notification_msg_text = f"Job № `{task_id}` initialized...\n\n"  
    
    notification_msg = await message.reply_text(notification_msg_text)
    await refresh_task_status(client, task_id, notification_msg=notification_msg)
    
@Client.on_message(filters.command(["reset"], prefixes="/"), group=1)
async def reset(client, message):
    delete_plugin_settings(plugin='txt2img', chat=message.from_user.id)