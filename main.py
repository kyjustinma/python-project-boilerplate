import os
import time
import signal
import sys

from sample.input_args import parse_arguments
from config.settings import config, logger


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)
    try:
        if input("\n Do you really want to quit? (y/n) >").lower().startswith("y"):
            logger.warn("Application ended gracefully")
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    inputArgs = parse_arguments()
    logger.debug(f"Logging level is at {inputArgs.verbose}")
    logger.info(f"Flask server on {config['FLASK_IP']}:{config['FLASK_PORT']}")
    while True:
        time.sleep(1)
        print("a")
