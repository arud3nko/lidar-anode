import logging
import socket
import asyncio
import uuid

from app import LidarSettings
from app.constants import LidarMessages
from app.lidar.exceptions import SocketConnectionException


logger = logging.getLogger(__package__)


class Lidar:
    def __init__(self,
                 ip:      str,
                 port:    int = LidarSettings.PORT.value,
                 timeout: int = LidarSettings.TIMEOUT.value):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        # self.client = socket.socket(socket.AF_INET,
        #                             socket.SOCK_STREAM)
        # self.client.settimeout(5)

    # async def _connect(self) -> None:
    #     """
    #     Подключение к сокету лидара
    #     :return:
    #     """
    #     try:
    #         logger.debug("connecting...")
    #         self.client.connect(
    #             (
    #                 self.ip,
    #                 self.port
    #             )
    #         )
    #     except socket.error as exception:
    #         logger.error(f"({self.ip}) Error occurred while trying to send request: {exception}")
    #         # raise SocketConnectionException
    #     else:
    #         logger.error(f"({self.ip}) Successfully connected to lidar")

    async def scan(self):
        while True:
            await asyncio.sleep(0.5)
            yield uuid.uuid4()
