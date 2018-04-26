import logging
import sys

DEFAULT_STREAM_LEVEL = logging.INFO
DEFAULT_FILE_LEVEL = logging.DEBUG

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def configure_logging(log_path: str = None,
                      stream_level: int = DEFAULT_STREAM_LEVEL,
                      file_level: int = DEFAULT_FILE_LEVEL):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    def add_handler(handler, level):
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    add_handler(logging.StreamHandler(sys.stdout), stream_level)
    if log_path is not None:
        add_handler(logging.FileHandler(log_path), file_level)
