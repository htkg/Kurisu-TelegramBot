
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram import Client, filters
from kurisu.core.database.methods import create_or_update_plugin_settings
from kurisu.cogs.dream.helpers import load_available_options

async def get_params(settings):
    keyboard = InlineKeyboard(row_width=2)
    keyboard.row(
        InlineButton(f'Orientation: {settings["orientation"]}', 'sd:orientation'),
        InlineButton(f'Sampler: {settings["sampler"]}', 'sd:sampler')
    )
    keyboard.row(
        InlineButton(f'Steps: {settings["steps"]}', 'sd:steps'),
        InlineButton(f'Count: {settings["batch_size"]}', 'sd:batch_size'),
        InlineButton(f'CFG Scale: {settings["cfg_scale"]}', 'sd:cfg_scale')
    )
    keyboard.row(
        InlineButton(f'Upscale: {settings["upscale"]}', 'sd:upscale'),
    )
    return keyboard


@Client.on_callback_query(filters.regex('^sd:'))
async def additional_settings(client, callback_query):
    options = load_available_options()

    if (callback_query.message.reply_to_message and
            callback_query.from_user.id != callback_query.message.reply_to_message.from_user.id):
        return await callback_query.answer("🚫 Permission denied",
                                           show_alert=True)

    key = callback_query.data.split(":")[1]

    if key not in options:
        return await callback_query.answer("🚫 Invalid option", show_alert=True)

    keyboard = InlineKeyboard(row_width=2)
    for option in options[key]:
        keyboard.row(InlineButton(f"{option}", f"change:{key}:{option}"))
        
    await callback_query.edit_message_text("✍️ Please choice settings below", reply_markup=keyboard)
    await callback_query.answer()

@Client.on_callback_query(filters.regex('^change:'))
async def process_change(client, callback_query):
    options = load_available_options()
    
    reply_to_msg = callback_query.message.reply_to_message
    
    if not callback_query.from_user.id == reply_to_msg.from_user.id:
        await callback_query.answer("🚫 Permission denied", show_alert=True)
        return

    key, value = callback_query.data.split(":")[1:]

    if value in ("False", "True"):
        value = True if value == "True" else False

    if key not in options or value not in options[key]:
        await callback_query.answer("🚫 Invalid option", show_alert=True)
        return

    pluginsettings, success = create_or_update_plugin_settings(plugin='txt2img', chat=reply_to_msg.from_user.id)
    settings = pluginsettings.settings
    settings[key] = value
    pluginsettings, success = create_or_update_plugin_settings(plugin='txt2img', chat=reply_to_msg.from_user.id, params=settings)

    kb = await get_params(settings)
    await callback_query.edit_message_text(f"✅ {key} set to {value}", reply_markup=kb)
    await callback_query.answer("👍")

