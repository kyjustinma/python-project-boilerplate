def hello_worker(handlers, arg1):
    import time
    import logging

    mp1_logger = logging.getLogger("MP1")

    """
    Runs a worker process that prints "hello" in an infinite loop.
    """
    while True:
        mp1_logger.critical(f"hello {arg1}")
        time.sleep(1)  # Pause for 1 second
