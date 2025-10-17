import os
import time
import logging
import logging.handlers
from typing import Literal
from enum import Enum
import yaml
from functools import lru_cache


@lru_cache(maxsize=1)
def load_logging_yaml(logging_yaml_path):
    with open(logging_yaml_path, "r") as f:
        return yaml.full_load(f)


def add_handler_if_not_exists(logger, handler):
    if not any(h.name == handler.name for h in logger.handlers):
        logger.addHandler(handler)


class PrefixedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """PrefixedTimedRotatingFileHandler
    This version of file handler will append the date before the .log file extension.
    The Default TimedRotatingFileHandler will append the date at the end on the file name.

    Args:
        logging (_type_): Default logging handler time rotating file handlers function
    """

    LOG_TYPES = ["debug", "info", "warning", "error", "critical"]

    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=7,
        encoding=None,
        delay=False,
        utc=False,
        atTime=None,
        errors=None,
        **kwargs,
    ):
        self.log_type = self.__get_log_type(kwargs, filename)
        self.prefix = self.__get_date_prefix()
        self.current_date = time.strftime("%Y-%m-%d")
        super().__init__(
            self.__generate_filename(filename),
            when,
            interval,
            backupCount,
            encoding,
            delay,
            utc,
            atTime,
            errors,
        )
        self.doRollover()

    def __get_log_type(self, init_kwargs, filename):
        if "level" in init_kwargs:
            return init_kwargs["level"].lower()

        for lgType in self.LOG_TYPES:
            if lgType.lower() in filename.lower():
                return lgType.lower()
        raise Exception(f"LogType was not defined for {filename}")

    def __get_date_prefix(self) -> str:
        return time.strftime("%Y-%m-%d")

    def __generate_filename(self, filename: str) -> str:
        """__generate_filename
        Generate the new formatted file name from the current file name
        filename: "./data/logs/<LOG_TYPE>.log"
        new_filename: "./data/logs/<yyyy-mm-dd>.<LOG_TYPE>.log"
        Args:
            filename (str): Existing file name

        Returns:
            str: New file name formatted
        """
        directory = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        base_name = ".".join(base_name.split(".")[-2:])
        return os.path.normpath(os.path.join(directory, self.prefix + "." + base_name))

    def shouldRollover(self, record) -> bool:
        """shouldRollover
        Overwrites logging.handlers.TimedRotatingFileHandler shouldRollover function
        Sets the new filename based on new prefix and check if you should roll over

        Args:
            record : record is not used, as we are just comparing times, but it is needed so
                      the method signatures are the same

        Returns:
            bool: If the log file should roll over
        """
        current_date = time.strftime("%Y-%m-%d")
        if current_date != self.current_date:
            self.prefix = self.__get_date_prefix()
            self.baseFilename = self.__generate_filename(self.baseFilename)
            self.current_date = current_date
            return True
        return False

    def doRollover(self) -> None:
        """doRollover
        Closes the current logging stream
        Sets up new stream to log to
        """
        if self.stream:
            self.stream.close()
        self.prefix = self.__get_date_prefix()
        self.baseFilename = self.__generate_filename(self.baseFilename)
        self.current_date = time.strftime("%Y-%m-%d")
        self.stream = self._open()
        if self.backupCount > 0:
            try:
                for s in self.getFilesToDelete():
                    logging.info(
                        f"[logging][doRollOver] Removing out of date ({self.backupCount}) files {s}"
                    )
                    os.remove(s)
            except Exception as e:
                logging.info(e)

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.
        """
        result = []
        dirName, baseName = os.path.split(self.baseFilename)  # dir, log_file
        fileNames = os.listdir(dirName)  # All logs
        n, e = os.path.splitext(baseName)
        _, log_type = n.split(".")

        for fileName in fileNames:
            if (
                not fileName.endswith(e)
                # or self.log_type not in fileName.lower()
                or f".{log_type}" not in fileName
            ):  # does have .log
                continue

            parts = fileName.split(".")
            for part in parts:
                if self.extMatch.match(part):
                    result.append(os.path.join(dirName, fileName))
                    break
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[: len(result) - self.backupCount]
        return result


class LoggingColours(str, Enum):
    ### Setting the colours
    RESET: str = "\x1b[0m"

    GREY: str = "\x1b[38;20m"
    YELLOW: str = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RED_BG = "\x1b[41;20m"

    BLACK = "\x1b[30m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"

    BRIGHT_BLACK: str = "\x1b[90m"  # Bright Black (Gray)
    BRIGHT_RED: str = "\x1b[91m"  # Bright Red
    BRIGHT_GREEN: str = "\x1b[92m"  # Bright Green
    BRIGHT_YELLOW: str = "\x1b[93m"  # Bright Yellow
    BRIGHT_BLUE: str = "\x1b[94m"  # Bright Blue
    BRIGHT_MAGENTA: str = "\x1b[95m"  # Bright Magenta
    BRIGHT_CYAN: str = "\x1b[96m"  # Bright Cyan
    BRIGHT_WHITE: str = "\x1b[97m"  # Bright White


class ColouredLoggingFormatter(logging.Formatter):
    """ColouredLoggingFormatter
    Based on logging.Formatter class
    Changes the colour of the Critical, Error and Warning logs
    """

    def __init__(
        self,
        fmt: str,
        logger_name: str,
        logger_colour: LoggingColours | None,
        colour_level: Literal[None, "level", "line"] = "level",
        level_colour_mapping: dict = {},
    ):
        """__init__ _summary_

        Args:
            fmt (str): Format for the coloured formatter
            logger_name (str): Name of the logger.
            logger_colour (LoggingColours | None]): The colour of the logger.
            level_colour_mapping (dict, optional): Colour mapping to the ASCII colour. Defaults to {}.
        """
        super().__init__(fmt)
        self.logger_name = logger_name
        self.colour_level = (
            colour_level.lower() if isinstance(colour_level, str) else None
        )
        self.level_colour_mapping = level_colour_mapping
        self.logger_colour = logger_colour if logger_colour else LoggingColours.BLUE
        self.level_colour_mapping.update(
            {
                logging.CRITICAL: LoggingColours.RED_BG,
                logging.ERROR: LoggingColours.BOLD_RED,
                logging.WARNING: LoggingColours.YELLOW,
                logging.INFO: LoggingColours.GREY,
                logging.DEBUG: LoggingColours.GREY,
                logging.NOTSET: LoggingColours.GREY,
                0: LoggingColours.GREY,
                "default": LoggingColours.GREY,
                "reset": LoggingColours.RESET,
            }
        )
        # Pre-compute coloured level names for speed
        self._level_cache = {
            logging.DEBUG: self.level_colour_mapping[logging.DEBUG]
            + "DEBUG"
            + LoggingColours.RESET,
            logging.INFO: self.level_colour_mapping[logging.INFO]
            + "INFO"
            + LoggingColours.RESET,
            logging.WARNING: self.level_colour_mapping[logging.WARNING]
            + "WARNING"
            + LoggingColours.RESET,
            logging.ERROR: self.level_colour_mapping[logging.ERROR]
            + "ERROR"
            + LoggingColours.RESET,
            logging.CRITICAL: self.level_colour_mapping[logging.CRITICAL]
            + "CRITICAL"
            + LoggingColours.RESET,
        }

    def _get_colored_line_prefix(self, levelno: int) -> str:
        """_get_colored_format
            Get the colour prefix for the log based on levelno

        Args:
            levelno (int): log level

        Returns:
            str: prefix for log level colour
        """
        return self.level_colour_mapping.get(levelno, "")

    def format(self, record):
        log_message = super().format(record)

        if self.colour_level == "level":
            # Replace only the LEVEL field
            if record.levelno in self._level_cache:
                log_message = log_message.replace(
                    record.levelname, self._level_cache[record.levelno], 1
                )

            # Colour the logger name if specified
            if self.logger_name and self.logger_name in log_message:
                log_message = log_message.replace(
                    self.logger_name,
                    self.logger_colour + self.logger_name + LoggingColours.RESET,
                    1,
                )

        elif self.colour_level == "line":
            # Wrap the whole line in the level's colour
            colour_prefix = self._get_colored_line_prefix(record.levelno)
            log_message = colour_prefix + log_message + LoggingColours.RESET

            # Special case: if logger_name should be differently coloured,
            # reset to its colour, then restore the line colour after it.
            if self.logger_name and self.logger_name in log_message:
                log_message = log_message.replace(
                    self.logger_name,
                    (
                        self.logger_colour + self.logger_name + LoggingColours.RESET,
                        colour_prefix,  # restore line colour
                    ),
                    1,
                )

        return log_message
