from pyrogram import Client
from dotenv import dotenv_values
from kurisu.core.logger import setup_logging

from loguru import logger

setup_logging(log_dir="logs", log_level="INFO", json_logs=False)

logger.info("Starting Kurisu...")
config = dotenv_values(".env")

app = Client(
    **config,
    plugins=dict(root="kurisu.cogs")
)