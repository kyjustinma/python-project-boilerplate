import os
import time
import signal
import sys
from multiprocessing import Process

from config.settings import ENV_CONFIG, logger
from flask_process import FlaskServer


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

    except KeyboardInterrupt or EOFError:
        print("Keyboard interrupt, quitting service")
        exit_functions()
        os._exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    for key, value in ENV_CONFIG.items():
        logger.info(f"{key}|{value}")

    # task_queue = Queue(maxsize=100)
    # task_list = Manager().list([])
    # task_dict = Manager().dict({})
    task_queue = None
    task_list = None
    task_dict = None

    ### Flask Server
    flask_arguments = {
        "flask_host": ENV_CONFIG["FLASK_IP"],
        "flask_port": ENV_CONFIG["FLASK_PORT"],
        "https": ENV_CONFIG["HTTPS"],
        "task_queue": task_queue,
        "task_dict": task_dict,
        "task_list": task_list,
    }
    sample_flask_process = (
        Process(  # Config will display twice as it will be loaded by this process
            target=FlaskServer, kwargs=flask_arguments, name="FlaskServer", daemon=True
        )
    ).start
    # FlaskServer(
    #     flask_host=ENV_CONFIG["FLASK_IP"],
    #     flask_port=ENV_CONFIG["FLASK_PORT"],
    #     https=ENV_CONFIG["HTTPS"],
    #     task_queue=task_queue,
    #     task_dict=task_dict,
    #     task_list=task_list,
    #     debugging=True,
    # )
    while True:
        time.sleep(1)
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warn")
        logger.error("Error")
        logger.critical("Critical")
