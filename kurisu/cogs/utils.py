from time import time
from pyrogram import Client, filters

commands_docs = {
    "dream": "Генерация изображения по промпту. Имеет два режима: txt2img, img2img. Настройки доступны через /settings",
    "booru": "Описывает приложенное изображение в стиле тэгов Danbooru",
    "tarot": "Расскладывает таро по кресту",
    "ping": "Жив ли бот?",
    "start": "Начало работы с ботом",
    "help": "Вызов справки",
    "settings": "Настройки бота",
    "v2t": "Преобразование голосового сообщения или аудиофайла до 50 МБ и меньше 120 секунд в текст",
    "sum": "Кратко описывает о чем были последние 30 сообщений",
}


@Client.on_message(filters.command(["ping"], prefixes="/"), group=1)
async def ping(client, message):
    start = time()
    reply = await message.reply_text("...", quote=True)
    delta_ping = time() - start
    await reply.edit_text(f"**Pong!** `{delta_ping * 1000:.2f} ms`")
    
@Client.on_message(filters.command(["start", "help"], prefixes="/"), group=1)
async def start(client, message):
    msg = "Привет! Добро пожаловать в бота. Пожалуйста подпишись на @salieri_chan.\n"
    
    for command, doc in commands_docs.items():
        msg += f"\n/{command} - {doc}"
    
    msg += "\n\n**Пассивные команды**\n- Ответ на сообщение вызывает переписку с ChatGPT\n- Автоматическая расшифровка голосовых сообщений\n\nЕсли у тебя есть какие-то предложения или вопросы, пиши мне по контактам из описания бота."
    
    await message.reply_text(msg) 