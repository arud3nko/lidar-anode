import logging

from app import constants

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename=f"./log/{__package__}.log")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(fmt=constants.LOGGING_FORMAT,
                              datefmt=constants.LOGGING_DATETIME)

handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(handler)
