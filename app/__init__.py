"""
required Python3.8
"""


from configparser import ConfigParser
from enum import Enum

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
