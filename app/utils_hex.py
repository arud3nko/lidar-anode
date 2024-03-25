"""

Дополнительные функции для использования шестнадцатеричной системы

"""
import asyncio

from asyncio import Queue
from typing import Optional, Callable, Awaitable, Any, List

from .lidar import Lidar, LidarParams, LidarFormulaeConstants
from .utils import convert_radial_to_ternary, calculate_length, make_split


def convert_hex_string_to_bytes_list(source: str) -> list:
    """

    Конвертирует строку из шестнадцатеричной системы в список байтов

    :param source: Строка в шестнадцатеричной системе
    :type source: str
    :return: Список байтов
    :rtype: list
    """
    return [int(source[i:i + 4], 16) for i in range(0, len(source), 4)]


async def process_hex_messages(message_queue: Queue,
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
                length=convert_hex_string_to_bytes_list(
                    source=make_hex_split(
                        value=message)
                ),
                z=_z
            )
            points.append(await callback(coords) if callback else coords)
            _z += LidarFormulaeConstants.Z.value
        except asyncio.TimeoutError:
            break

    return points


def make_hex_split(value: str) -> str:
    """
    Эта функция делает срез байтов, выбирая необходимые данные

    :param value:
        Исходный поток байтов

    :return: Данные для расчета длин
    :rtype: bytes

    """
    return value[182:3546]
