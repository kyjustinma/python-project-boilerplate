import os
import time
import logging
import logging.handlers
from typing import Literal


class PrefixedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """PrefixedTimedRotatingFileHandler
    This version of file handler will append the date before the .log file extension.
    The Default TimedRotatingFileHandler will append the date at the end on the file name.

    Args:
        logging (_type_): Default logging handler time rotating file handlers function
    """

    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
    ):
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
        )
        self.getFilesToDelete()

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
            self.stream = None
        self.prefix = self.__get_date_prefix()
        self.baseFilename = self.__generate_filename(self.baseFilename)
        self.current_date = time.strftime("%Y-%m-%d")
        self.stream = self._open()
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                print(f"Removing files {s}")
                os.remove(s)

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.

        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        # See bpo-44753: Don't use the extension when computing the prefix.
        n, e = os.path.splitext(baseName)
        prefix = n + "."
        plen = len(prefix)

        date, log_type, file_end = baseName.split(".")
        for fileName in fileNames:
            if self.namer is None:
                # Our files will always start with baseName
                if not fileName.startswith(baseName):
                    continue
            else:
                # Our files could be just about anything after custom naming, but
                # likely candidates are of the form
                # foo.log.DATETIME_SUFFIX or foo.DATETIME_SUFFIX.log
                if (
                    not fileName.startswith(baseName)
                    and fileName.endswith(e)
                    and len(fileName) > (plen + 1)
                    and not fileName[plen + 1].isdigit()
                ):
                    continue

            if log_type in fileName:
                # Correct log type
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


class ColouredLoggingFormatter(logging.Formatter):
    """ColouredLoggingFormatter
    Based on logging.Formatter class
    Changes the colour of the Critical, Error and Warning logs
    """

    ### Setting the colours
    reset = "\x1b[0m"

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    red_bg = "\x1b[41;20m"

    black = "\x1b[30m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    cyan = "\x1b[36m"
    white = "\x1b[37m"

    def __init__(
        self,
        fmt: str,
        colour_level: Literal[None, "Level", "Line"] = False,
        colour_logger_name: tuple = None,
        level_colour_mapping: dict = {},
    ):
        """__init__ _summary_

        Args:
            fmt (str): Format for the coloured formatter
            colour_level (bool, optional): Colour the logger level. Defaults to False.
            colour_logger_name (tuple, optional): ("logger_name":<ASCII_Colour> | None (for blue)). Defaults to None.
            level_colour_mapping (dict, optional): Colour mapping to the ASCII colour. Defaults to {}.
        """
        super().__init__(fmt)
        self.colour_level = colour_level
        self.level_colour_mapping = level_colour_mapping
        self.colour_logger_name = colour_logger_name
        if self.colour_logger_name is not None:
            self.logger_name = self.colour_logger_name[0]
            try:
                if self.colour_logger_name[1] is None:
                    self.logger_name_colour = self.blue
                else:
                    self.logger_name_colour = self.colour_logger_name[1]
            except Exception as e:
                self.logger_name_colour = self.blue

        self.level_colour_mapping.update(
            {
                logging.CRITICAL: self.red_bg,
                logging.ERROR: self.bold_red,
                logging.WARNING: self.yellow,
                logging.INFO: self.grey,
                logging.DEBUG: self.grey,
                logging.NOTSET: self.grey,
                0: self.grey,
                "default": self.grey,
                "reset": self.reset,
            }
        )

    def _get_colored_format(self, levelno: int) -> str:
        """_get_colored_format
            Get the colour prefix for the log based on levelno

        Args:
            levelno (int): log level

        Returns:
            str: prefix for log level colour
        """
        return self.level_colour_mapping[levelno]

    def __color_format_section(self, section: str, colour: str) -> str:
        """__color_format_section
            formats a section of string according to the levelno

        Args:
            section:(str): section of string
            levelno (int): log level

        Returns:
            str: section with colour format
        """
        return colour + section + self.level_colour_mapping["reset"]

    def format(self, record: logging.LogRecord) -> str:
        """format
          Adds colour and colour reset to log string
        Args:
            record (logging.LogRecord): Log record data

        Returns:
            str: Returns the string to be outputted in console
        """
        log_message = super().format(record)
        if self.colour_level == "Level":
            log_message = super().format(record)
            log_message = log_message.replace(
                record.levelname,
                self.__color_format_section(
                    record.levelname, self.level_colour_mapping[record.levelno]
                ),
                1,
            )
        elif self.colour_level == "Line":
            log_message = (
                self._get_colored_format(record.levelno)
                + super().format(record)
                + self.reset
            )
        elif self.colour_logger_name is not None:
            log_message = log_message.replace(
                self.logger_name,
                self.__color_format_section(self.logger_name, self.logger_name_colour),
                1,
            )

        return log_message
