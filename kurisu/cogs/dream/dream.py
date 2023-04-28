import json
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from kurisu.core.database.methods import create_or_update_plugin_settings, get_plugin_settings, get_task, delete_plugin_settings
from kurisu.cogs.dream.runpod_reqs import async_run, check_status
from kurisu.cogs.dream.helpers import process_response_raw, get_params
from loguru import logger
from pyrogram.errors.exceptions.flood_420 import FloodWait

with open('kurisu/cogs/dream/data/default_params.json') as f:
    default_params = json.load(f)


async def get_image_size(orientation):
    if orientation == "portrait":
        return 512, 768
    elif orientation == "landscape":
        return 768, 512
    else:
        return 512, 512

async def refresh_task_status(client, task_id, notification_msg):
    iteration = 0
    prev_status = None
    
    while True:
        results = await check_status(task_id)
        
        if results['status'] != prev_status:
            task_db = get_task(task_guid=task_id)
            task_db.status = results["status"]
            try:
                task_db.parameters = results['output']['parameters']
                task_db.infotext = results['output']['infotext']
            except:
                pass
            task_db.save()
            prev_status = results['status']

        if results['status'] == "IN_PROGRESS":
            try:
                iteration += 1
                await notification_msg.edit_text(f"Job № `{task_id}` is in progress...\n\nHeartbeat: `{iteration}` (if heartbeat stops, then task suddenly died.)")
            except Exception as e:
                pass

        elif results["status"] == "COMPLETED":
            images = process_response_raw(results['output'])
            execution_time = int(results['executionTime']) / 1000
            cost = 0.0002 * (execution_time + 5)
            sampler = results['output']['parameters']['sampler_index']
            prompt = results['output']['parameters']['prompt']
            enable_hr = results['output']['parameters']['enable_hr']
            hr_scale = enable_hr and results['output']['parameters']['hr_scale'] or 1
            width = results['output']['parameters']['width'] * hr_scale
            height = results['output']['parameters']['height'] * hr_scale
            caption = f"""**Job № `{task_id}` done in {execution_time} seconds.**\n\n**Prompt:** `{prompt}`\n**Sampler:** {sampler}\n\n**Upscaler:** {enable_hr}\n**Width:** {width}\n**Height:** {height}\n\nJob cost: `{round(cost, 4)}` USD"""

            images[0].caption = caption
            
            logger.success(f"Job № `{task_id}` done in {execution_time} seconds.")
            
            try:
                await client.send_media_group(chat_id=task_db.chat_id, reply_to_message_id=task_db.message_id, media=images)
            except FloodWait:
                await asyncio.sleep(30)
                await client.send_media_group(chat_id=task_db.chat_id, reply_to_message_id=task_db.message_id, media=images)
                
            await notification_msg.delete()
            break

        elif results["status"] == "FAILED":
            logger.error(f"Job № `{task_id}` failed.")
            await notification_msg.edit_text(f"Job № `{task_id}` failed.")
            break

        await asyncio.sleep(5)

@Client.on_message(filters.command(["dream"], prefixes="/") &~ filters.channel, group=1)
async def txt2img(client, message):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    pluginsettings = get_plugin_settings(plugin='txt2img', chat=user_id)
    
    if not pluginsettings:
        create_or_update_plugin_settings(plugin='txt2img', chat=user_id, params=default_params)
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

    task_id = await async_run(payload=payload, user_id=user_id, chat_id=message.chat.id, message_id=message.id)

    notification_msg_text = f"Job № `{task_id}` initialized with parameters:\n"  
    for key, value in generation_options.items():
        notification_msg_text += f"\n**{key}:** `{value}`"
    notification_msg_text += "\n\n**Please wait... It launches Docker container first, that could take up to 15 seconds.**"

    notification_msg = await message.reply_text(notification_msg_text)
    await refresh_task_status(client, task_id, notification_msg=notification_msg)

    
@Client.on_message(filters.command(["reset"], prefixes="/"), group=1)
async def reset(client, message):
    delete_plugin_settings(plugin='txt2img', chat=message.from_user.id)