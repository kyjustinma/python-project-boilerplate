import logging.handlers
import os
import time


class PrefixedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
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
        self.prefix = self._get_date_prefix()
        self.current_date = time.strftime("%Y-%m-%d")
        super().__init__(
            self._generate_filename(filename),
            when,
            interval,
            backupCount,
            encoding,
            delay,
            utc,
        )

    def _get_date_prefix(self):
        return time.strftime("%Y-%m-%d")

    def _generate_filename(self, filename: str) -> str:
        directory = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        base_name = ".".join(base_name.split(".")[-2:])
        return os.path.join(directory, self.prefix + "." + base_name)

    def shouldRollover(self, _) -> bool:
        current_date = time.strftime("%Y-%m-%d")
        if current_date != self.current_date:
            self.prefix = self._get_date_prefix()
            self.baseFilename = self._generate_filename(self.baseFilename)
            self.current_date = current_date
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.prefix = self._get_date_prefix()
        self.baseFilename = self._generate_filename(self.baseFilename)
        self.current_date = time.strftime("%Y-%m-%d")
        self.stream = self._open()
