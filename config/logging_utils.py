import os
import time
import logging
import logging.handlers


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
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    red_bg = "\x1b[41;20m"
    reset = "\x1b[0m"

    def __find_formatter_type(self, yaml_config: dict, logger_name: str) -> str:
        """__find_formatter_type
            Finds the format of the current logger based on the .yaml file ("default", "simple", "detailed")

        Args:
            root_logger (logging.Logger): Current Logger pulled from the yaml file
            yaml_config (dict): yaml config that was loaded

        Returns:
            str: root_logger format type
        """

        # Default format is below
        format_string = (
            r"%(asctime)s | [%(levelname)7s][%(module)s - %(funcName)s] | %(message)s"
        )
        try:
            logger_level = yaml_config["loggers"][logger_name]["level"]
            console_handlers = [
                yaml_handlers
                for yaml_handlers in yaml_config["handlers"]
                if "console" in yaml_handlers.lower()
            ]
            for valid_handlers in console_handlers:
                if yaml_config["handlers"][valid_handlers]["level"] == logger_level:
                    formatter_type = yaml_config["handlers"][valid_handlers][
                        "formatter"
                    ]
                    return yaml_config["formatters"][formatter_type]["format"]
        except Exception as e:
            print(f"Failed to find default format string, {e}")
        return format_string

    def __init__(
        self,
        yaml_config: dict,
        logger_name: str,
    ):
        """__init__
        Args:
            format: The format the logger should output in
        """
        super().__init__(self.__find_formatter_type(yaml_config, logger_name))

    def _get_colored_format(self, levelno: int) -> str:
        """_get_colored_format
            Get the colour prefix for the log based on levelno

        Args:
            levelno (int): log level

        Returns:
            str: prefix for log level colour
        """
        if levelno >= logging.CRITICAL:
            return self.red_bg
        elif levelno >= logging.ERROR:
            return self.bold_red
        elif levelno >= logging.WARNING:
            return self.yellow
        else:
            return self.grey

    def format(self, record: logging.LogRecord) -> str:
        """format
          Adds colour and colour reset to log string
        Args:
            record (logging.LogRecord): Log record data

        Returns:
            str: Returns the string to be outputted in console
        """
        log_message = (
            self._get_colored_format(record.levelno)
            + super().format(record)
            + self.reset
        )
        return log_message
