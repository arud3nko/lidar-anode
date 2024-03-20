"""

В этом модуле реализованы вспомогательные синхронные функции

Сделал последовательно, хотя изначально придумал класс Point, содержащий изначальные значения в радиальной СК
и реализующий методы для получения длины, угла и преобразования в двумерную СК,
но с учетом количества точек это оказалось просто невыгодно по памяти, поэтому ФП здесь больше подойдет

"""
import math

from typing import List


def convert_radial_to_ternary(length: list, z: float) -> List[tuple]:
    """

    Конвертирует координаты из радиальной в трехмерную СК

    :param length: Список значений длин
    :type length: list
    :param z: Константа Z, увеличивающаяся с каждой итерацией на расстояние между срезами
    :type z: float
    :return: Список кортежей с координатами X, Y, Z
    :rtype: List[tuple]
    """
    coords = []

    for _length, _angle in zip(length,
                               [calculate_angle(x) for x in range(0, len(length))]):
        if not _length:
            continue

        radian_angle = _angle * math.pi / 180
        x = math.cos(radian_angle) * _length
        y = math.sin(radian_angle) * _length

        coords.append((x, y, z))

    return coords


def calculate_length(data: bytes) -> list:
    """

    Вычисляет значение длины (берет срез два байта)

    :param data: Поток байтов
    :type data: bytes
    :return: Список значений длин
    :rtype: list
    """
    result = []
    while len(data) >= 2:
        result.append(float(int.from_bytes(data[:2], byteorder="little")) / 10000)
        data = data[2:]
    return result


def calculate_angle(x: int) -> float:
    """

    Высчитывает значение угла

    :param x: Число
    :type x: int
    :return: Значение угла
    :rtype: float
    """
    return 55 + x * 0.0833


def make_split(value: bytes) -> bytes:
    """
    Эта функция делает срез байтов, выбирая необходимые данные

    :param value:
        Исходный поток байтов

    :return: Данные для расчета длин
    :rtype: bytes

    """
    return value[91:1773]
