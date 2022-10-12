import os
import logging
from sample.input_args import parse_arguments
from config.settings import config, logger


print(os.getcwd())

if __name__ == "__main__":
    inputArgs = parse_arguments()
    logger.debug(f"Logging level is at {inputArgs.verbose}")
    logger.info(f"Flask server on {config['FLASK_IP']}:{config['FLASK_PORT']}")
    logger.debug(f"PORT Status:")