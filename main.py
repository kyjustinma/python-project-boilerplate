import logging
from config.settings import config
from sample.input_args import parse_arguments


if __name__ == "__main__":
    inputArgs = parse_arguments()
    logging.debug(f"Logging level is at {inputArgs.verbose}")
    logging.info(f"Flask server on {config['FLASK_IP']}:{config['FLASK_PORT']}")
