import logging
import os
import sys

DEFAULT_NAME = 'root'
DEFAULT_STREAM_LEVEL = logging.INFO
DEFAULT_FILE_LEVEL = logging.DEBUG
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logger(name: object = None,
                 log_dir: object = None,
                 stream_level: object = DEFAULT_STREAM_LEVEL,
                 file_level: object = DEFAULT_FILE_LEVEL,
                 format: object = DEFAULT_FORMAT) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    def add_handler(handler, level):
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format))
        logger.addHandler(handler)

    add_handler(logging.StreamHandler(sys.stdout), stream_level)

    if log_dir is not None:
        file_path = os.path.join(log_dir, f'{name or DEFAULT_NAME}.log')
        add_handler(logging.FileHandler(file_path, mode='w'), file_level)

    return logger


def disable_logging(name: str = None):
    logger = logging.getLogger(name)
    logger.disabled = True
