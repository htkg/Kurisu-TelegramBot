from pyrogram import Client
from kurisu.core.logger import setup_logging
import yaml
from loguru import logger


setup_logging(log_dir="logs", log_level="INFO", json_logs=False)


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

db_cfg = config["database"]
tg_cfg = config["telegram"]

logger.info("Starting Kurisu...")
plugins_folder = dict(root="kurisu.cogs")

app = Client(
    **tg_cfg,
    plugins=plugins_folder
)