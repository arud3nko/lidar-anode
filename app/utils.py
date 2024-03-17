"""

В этом модуле реализованы вспомогательные синхронные функции

"""


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


def calculate_angles(length: int) -> list:
    """

    Генерирует массив значений угла исходя из числа элементов массива длин

    :param length: Число значений
    :type length: int
    :return: Список значений углов
    :rtype: list
    """
    return [(55 + (i * 0.0833)) for i in range(0, length - 1)]


def make_split(value: bytes) -> bytes:
    """
    Эта функция делает срез байтов, выбирая необходимые данные

    :param value:
        Исходный поток байтов

    :return: Данные для расчета длин
    :rtype: bytes

    """
    return value[91:1773]
