from pykeyboard import InlineKeyboard, InlineButton
from pyrogram import Client, filters
from kurisu.core.database.methods import create_or_update_plugin_settings
import json


async def get_params(settings):
    keyboard = InlineKeyboard(row_width=2)
    keyboard.row(
        InlineButton(f'Orientation: {settings["orientation"]}', f'sd:orientation'),
        InlineButton(f'Sampler: {settings["sampler"]}', f'sd:sampler'))
    keyboard.row(
        InlineButton(f'Steps: {settings["steps"]}', f'sd:steps'),
        InlineButton(f'Count: {settings["batch_size"]}', f'sd:batch_size'),
        InlineButton(f'CFG Scale: {settings["cfg_scale"]}', f'sd:cfg_scale'))
    keyboard.row(
        InlineButton(f'Upscale: {settings["upscale"]}', f'sd:upscale'),
    )
    return keyboard


@Client.on_callback_query(filters.regex('^sd:'))
async def additional_settings(client, callback_query):
    with open('kurisu/cogs/dream/options.json') as f:
        options = json.load(f)

    if (callback_query.message.reply_to_message and
            callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id):
        return await callback_query.answer("🚫 Permission denied",
                                           show_alert=True)

    key = callback_query.data.split(":")[1]

    if key not in options:
        return await callback_query.answer("🚫 Invalid option", show_alert=True)

    keyboard = InlineKeyboard(row_width=2)
    for option in options[key]:
        keyboard.row(
            InlineButton(f"{option}", f"change:{key}:{option}"))
    await callback_query.edit_message_text(f"✍️ Please choice settings below", reply_markup=keyboard)
    await callback_query.answer()


@Client.on_callback_query(filters.regex('^change:'))
async def process_change(client, callback_query):
    if callback_query.message.reply_to_message and callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id:
        return await callback_query.answer("🚫 Permission denied",
                                           show_alert=True)

    with open('kurisu/cogs/dream/options.json') as f:
        available_options = json.load(f)

    key, value = callback_query.data.split(":")[1:]

    if value == "False":
        value = False
    elif value == "True":
        value = True

    print(type(value))
    print(type(key))
    if key not in available_options or value not in available_options[key]:
        return await callback_query.answer("🚫 Invalid option", show_alert=True)


    pluginsettings, success = create_or_update_plugin_settings(plugin='txt2img', chat=callback_query.message.reply_to_message.from_user.id)
    settings = pluginsettings.settings
    settings[key] = value
    pluginsettings, success = create_or_update_plugin_settings(plugin='txt2img', chat=callback_query.message.reply_to_message.from_user.id, params=settings)

    await callback_query.answer("👍")
    kb = await get_params(settings)
    await callback_query.edit_message_text(f"✅ {key} set to {value}", reply_markup=kb)
