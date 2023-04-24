from loguru import logger
import logging
import sys
import os
from datetime import datetime

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging(log_dir: str, log_level: int, json_logs: bool):
    os.makedirs(log_dir, exist_ok=True)

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)
    
    for name in logging.root.manager.loggerDict.keys():
        logger_instance = logging.getLogger(name)
        logger_instance.handlers = []
        logger_instance.propagate = True

    current_time = datetime.now().strftime("%Y-%m-%d")
    log_file_name = f"{current_time}.log"

    logger.configure(handlers=[
        {"sink": sys.stdout, "colorize": True, "serialize": json_logs},
        {"sink": os.path.join(log_dir, log_file_name), "serialize": json_logs, "rotation": "100 MB", "compression": "zip"}
    ])
