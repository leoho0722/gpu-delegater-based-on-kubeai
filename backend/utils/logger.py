import os
import sys
from datetime import datetime
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    StreamHandler,
    getLogger
)
from logging.handlers import RotatingFileHandler

from .constants.format import MiB


class ColorfulLoggingFormatter(Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s [%(levelname)s][%(module)s - %(funcName)s:%(lineno)d] %(message)s"

    FORMATS = {
        DEBUG: grey + format + reset,
        INFO: grey + format + reset,
        WARNING: yellow + format + reset,
        ERROR: red + format + reset,
        CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(
            fmt=log_fmt,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        return formatter.format(record)


class PlainTextLoggingFormatter(Formatter):

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)s][%(module)s - %(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


class KubeAIGPUDelegateLogger:

    def __init__(self, log_dir: str = "logs"):
        """Initialize KubeAI GPU Delegater Logger Instance

        Args:
            log_dir (str): The directory path to store the log file
        """

        self.log_dir = log_dir

        self.logger = getLogger("KubeAI GPU Delegater")
        self.logger.setLevel(DEBUG)

        colorful_formatter = ColorfulLoggingFormatter()
        console_handler = StreamHandler(sys.stdout)
        console_handler.setFormatter(colorful_formatter)
        console_handler.setLevel(DEBUG)

        log_filename_prefix = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        totay_log_dir = self.create_totay_log_dir(self.log_dir)
        log_filename = f"{totay_log_dir}/{log_filename_prefix}-gpu-delegater.log"
        plaintext_formatter = PlainTextLoggingFormatter()
        file_handler = RotatingFileHandler(
            filename=log_filename,
            mode="a",
            maxBytes=10 * MiB,
            backupCount=999999,
            encoding="utf-8"
        )
        file_handler.setFormatter(plaintext_formatter)
        file_handler.setLevel(DEBUG)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def getLogger(self):
        return self.logger

    def create_totay_log_dir(self, log_dir: str = "logs"):
        """檢查今天日期的 Log 目錄是否存在，若不存在則進行建立

        Args:
            log_dir (`str`): Log 目錄

        Returns:
            totay_log_dir (`str`): 今天日期的 Log 目錄路徑
        """

        cwd = os.getcwd()
        totay_date = datetime.now().strftime("%Y-%m%d")
        totay_log_dir = f"{cwd}/{log_dir}/{totay_date}"
        if not os.path.exists(totay_log_dir):
            os.makedirs(totay_log_dir)

        return totay_log_dir
