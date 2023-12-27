import os
import time
import signal
import sys

# from config.parse_arguments import parse_arguments
from config.settings import env_config, logger
import config.parse_arguments as argParse


def exit_functions():
    print("Goodbye cruel world")


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)
    try:
        if input("\n Do you really want to quit? (y/n) >").lower().startswith("y"):
            logger.warning("Application ended gracefully")
            exit_functions()
            os._exit(0)

    except KeyboardInterrupt:
        logger.error("Keyboard interrupt, quitting service")
        exit_functions()
        os._exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    inputArgs = argParse.parse_arguments()
    for key, value in env_config.items():
        logger.debug(key, value)

    while True:
        time.sleep(1)
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warn")
        logger.error("Error")
