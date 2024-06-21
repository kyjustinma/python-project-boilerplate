import multiprocessing
import os
import subprocess
import time
import signal
import sys
import config
from datetime import datetime
from multi_process import hello_worker
import logging


if __name__ == "__main__":
    from config.settings import ENV_CONFIG, logger, STANDARD_CONSOLE_HANDLER

    for key, value in ENV_CONFIG.items():
        logger.info(f"{key}|{value}")

    # Create a new handler with the same configuration
    mp1_logger = logging.getLogger("MP1")
    mp1_logger.setLevel(logger.level)
    for handler in logger.handlers:
        print(handler)
        if "console" in handler.name:
            mp1_logger.handlers.append(handler)
        if (
            isinstance(handler, logging.StreamHandler)
            and handler.level == mp1_logger.level
        ):
            logger_formatter = handler.formatter

    temp_mp1_handler = [
        config.logging_utils.PrefixedTimedRotatingFileHandler(
            filename="./data/logs/.mp1.log",
            when="midnight",
            backupCount=7,
        )
    ]
    for mp1_file_handlers in temp_mp1_handler:
        mp1_file_handlers.setLevel(mp1_logger.level)
        mp1_file_handlers.setFormatter(STANDARD_CONSOLE_HANDLER.formatter)
        mp1_logger.handlers.append(mp1_file_handlers)

    for handler in mp1_logger.handlers:
        print("MP1 ", handler)

    arg1 = 20
    p = multiprocessing.Process(target=hello_worker, args=(mp1_logger.handlers, arg1))
    p.start()
    while True:
        time.sleep(1)
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warn")
        logger.error("Error")
        logger.critical("Critical")
        # mp1_logger.critical('Hello world')
