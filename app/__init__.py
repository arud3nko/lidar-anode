"""
required Python3.8
"""

import logging

from configparser import ConfigParser
from enum import Enum


LOGGING_FORMAT = "%(levelname)s %(name)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s"
LOGGING_DATETIME = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename=f"./log/{__package__}.log")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(fmt=LOGGING_FORMAT,
                              datefmt=LOGGING_DATETIME)

handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(handler)

config = ConfigParser()
config.read("conf.ini")


class CarriageSettings(Enum):
    """
    Параметры каретки
    """
    MOVE_TIME = float(config["CARRIAGE"]["CarriageReturnTime"])
    COM_PORT = str(config["CARRIAGE"]["COMPort"])
    RATE = int(config["CARRIAGE"]["Rate"])
    TIMEOUT = float(config["CARRIAGE"]["ReadTimeout"])


class LidarSettings(Enum):
    """
    Параметры лидаров общие
    """
    PORT = int(config["LIDAR"]["PORT"])
    TIMEOUT = int(config["LIDAR"]["TIMEOUT"])


class LidarSettings1(Enum):
    """
    Параметры лидара 1
    """
    IP = str(config["LIDAR1"]["IP"])


class LidarSettings2(Enum):
    """
    Параметры лидара 2
    """
    IP = str(config["LIDAR2"]["IP"])
