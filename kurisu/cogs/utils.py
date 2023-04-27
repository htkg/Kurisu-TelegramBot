from time import time
from pyrogram import Client, filters

@Client.on_message(filters.command(["ping", "start", "help"], prefixes="/"), group=1)
async def ping(client, message):
    """Pong!"""
    
    start = time()
    reply = await message.reply_text("...", quote=True)
    delta_ping = time() - start
    await reply.edit_text(f"**Pong!** `{delta_ping * 1000:.2f} ms`")
    

@Client.on_message(filters.command(["ping", "start", "help"], prefixes="/"), group=1)
async def test(client, message):
    """test!"""
    
    start = time()
    reply = await message.reply_text("...", quote=True)
    delta_ping = time() - start
    await reply.edit_text(f"**Pong!** `{delta_ping * 1000:.2f} ms`")