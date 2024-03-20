"""

В этом модуле реализован основной функционал ПС

"""
import asyncio

from typing import Optional, Callable, Awaitable, Any, List
from asyncio import Queue

from .lidar import Lidar, LidarParams, LidarFormulaeConstants
from .utils import convert_radial_to_ternary, calculate_length, make_split


async def lidar_worker(number: int,
                       ip: str,
                       port: int,
                       message_queue: Queue) -> ...:
    """

    Lidar coroutine worker

    :param number: Номер лидара
    :type number: int
    :param ip: IP лидара
    :type ip: str
    :param port: Порт лидара
    :type port: int
    :param message_queue: Асинхронная очередь для записи полученных с лидара сообщений
        - разные очереди для разных лидаров!
    :type message_queue: Queue
    :return:
    :rtype:
    """
    async with Lidar(params=LidarParams(ip=ip,
                                        port=port)) as lidar:
        async for message in await lidar.scan():
            await message_queue.put((number, message))


async def process_messages(message_queue: Queue,
                           callback: Optional[Callable[[List[tuple]], Awaitable[Any]]] = None) -> List[List[tuple]]:
    """

    Асинхронно обрабатывает попадающие в очередь сообщения
    При достижении таймаута прерывается - значит сообщения кончились

    :param message_queue: Очередь сообщений - разные очереди для разных лидаров!
    :type message_queue: Queue
    :param callback: Асинхронная callback-функция для каждого среза,
        в качестве аргумента обязательно принимающая список кортежей
        (тип, возвращаемый функцией-обработчиком)
    :type callback: Optional[Callable[[List[tuple]], Awaitable[Any]]]
    :return: Массив (для каждого среза) массивов кортежей с координатами точек
        [[(x, y, z), (x, y, z)], [(x, y, z)] ...]
    :rtype: List[List[tuple]]
    """
    _z = LidarFormulaeConstants.Z.value
    points = []
    while True:
        try:
            number, message = await asyncio.wait_for(message_queue.get(), timeout=1)

            coords = convert_radial_to_ternary(
                length=calculate_length(
                    data=make_split(
                        value=message)
                ),
                z=_z
            )
            points.append(await callback(coords) if callback else coords)
            _z += LidarFormulaeConstants.Z.value
        except asyncio.TimeoutError:
            break

    return points
