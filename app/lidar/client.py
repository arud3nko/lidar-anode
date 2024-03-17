"""

Здесь реализован асинхронный клиент для сокета

"""

import asyncio

from typing import Union

from .models import LidarParams


class AsyncSocketClient:
    """

    Асинхронный клиент для сокета

    """
    def __init__(self,
                 params: LidarParams):
        """
        init
        """
        self._ip = params.ip
        self._port = params.port
        self._timeout = params.timeout

    async def __aenter__(self):
        await self._connect()
        return self._reader, self._writer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

    async def _connect(self):
        """

        Подключение к сокету

        """
        self._reader, self._writer = await asyncio.open_connection(
            self._ip,
            self._port
        )

    async def write(self, message: Union[str, bytes]):
        if isinstance(message, str):
            message = message.encode()

        self._writer.write(message)
        await self._writer.drain()

    async def read(self):
        """
        Чтение сообщений из сокета
        """
        while True:
            data = await self._reader.read(1024)
            if not data:
                break
            yield data

