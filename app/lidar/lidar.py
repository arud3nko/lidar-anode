import asyncio
import collections
import logging

from .client import AsyncSocketClient
from .exceptions import SocketConnectionException
from .models import LidarParams
from .constants import LidarMessages

logger = logging.getLogger(__package__)


class Lidar(AsyncSocketClient):
    def __init__(self,
                 params: LidarParams):
        super().__init__(params=params)
        self.__scanning_in_progress = False

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__scanning_in_progress:
            await self.stop()
            await asyncio.sleep(0.1)
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def scan(self) -> collections.AsyncIterable:
        self.__scanning_in_progress = True
        await super().write(LidarMessages.MESSAGE_START_MES.value)
        await super().write(LidarMessages.MESSAGE_START_FAST.value)
        return super().read()

    async def stop(self):
        await super().write(LidarMessages.MESSAGE_STOP_FAST.value)
        await super().write(LidarMessages.MESSAGE_STANDBY.value)