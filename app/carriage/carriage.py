"""
Модуль для управления кареткой
"""

import logging
import collections

from typing import Optional, Union

import serial
from serial import SerialException, SerialTimeoutException

from .exceptions import MoveException, MoveRequestException, MoveResponseException
from .constants import Move, MoveResponsesDevice1, MoveResponsesDevice2, MoveStages
from .models import CarriageParams

logger = logging.getLogger(__package__)


class Carriage:
    """
    Управление кареткой
    """
    def __init__(self,
                 params:        CarriageParams,
                 parity:        str = serial.PARITY_NONE,
                 stop_bits:     int = serial.STOPBITS_ONE,
                 bytesize:      int = serial.EIGHTBITS,
                 write_timeout: Optional[Union[int, float]] = None
                 ):
        """
        При инициализации создаем экземпляр клиента соединения с кареткой по COM-порту
        """
        try:
            self.client = serial.Serial(
                port=params.port,
                baudrate=params.baudrate,
                timeout=params.timeout,
                parity=parity,
                stopbits=stop_bits,
                bytesize=bytesize,
                write_timeout=write_timeout
            )
        except SerialException as exception:
            logger.critical(msg=f"Error occurred while trying to connect serial port carriage: "
                                f"{exception.strerror}")
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Закрываем соединение, если получаем ошибку - принудительно закрываем порт
        """
        try:
            del self.client
        except SerialException:
            self.client.close()

    async def move(self) -> collections.AsyncIterable:
        """
        Цикл движения каретки
            1) Посылаем команду на старт
            2) Ждем ответа от 1-го датчика о выполнении
            3) Опрашиваем 2-й датчик
            4) Ждем ответа от 2-го датчика о выполнении
             > Посылаем команду СТОП
             > Ждем ответа от 1-го датчика о выполнении
             > Опрашиваем 2-й датчик
             > Ждем ответа от 2-го датчика о выполнении
            5) Посылаем команду на возврат
            6) Ждем ответа от 1-го датчика о выполнении
            7) Опрашиваем 2-й датчик
            8) Ждем ответа от 2-го датчика о выполнении
        """
        try:
            await self.__send_request(
                request=Move.START.value
            )  # запрос на старт (общий)

            yield MoveStages.STARTED.value

            await self.__wait_for_response(
                expected=bytes(MoveResponsesDevice1.MOVE_COMPLETED.value)
            )  # ожидание ответа 1-й

            await self.__send_request(
                request=MoveResponsesDevice2.REQUEST.value
            )  # опрос 2-й

            await self.__wait_for_response(
                expected=bytes(MoveResponsesDevice2.MOVE_COMPLETED.value)
            )  # ожидание ответа 2-й

            yield MoveStages.MOVED.value

            await self.__send_request(
                request=Move.STOP.value
            )  # запрос на СТОП

            await self.__wait_for_response(
                expected=bytes(MoveResponsesDevice1.STOP.value)
            )  # ожидание ответа 1-й

            await self.__send_request(
                request=MoveResponsesDevice2.REQUEST.value
            )  # опрашиваем 2-й

            await self.__wait_for_response(
                expected=MoveResponsesDevice2.STOP.value
            )  # ожидаем ответа 2-й

            yield MoveStages.STOPPED.value

            await self.__send_request(
                request=Move.RETURN.value
            )  # запрос на возврат

            await self.__wait_for_response(
                expected=bytes(MoveResponsesDevice1.MOVE_COMPLETED.value)
            )  # ожидание ответа от 1-й

            await self.__send_request(
                request=MoveResponsesDevice2.REQUEST.value
            )  # опрос 2-й

            await self.__wait_for_response(
                expected=bytes(MoveResponsesDevice2.MOVE_COMPLETED.value)
            )  # ожидание ответа от 2-й

            yield MoveStages.RETURNED.value

        except (MoveRequestException, MoveResponseException) as exc:
            raise MoveException from exc

    async def __wait_for_response(self, expected: bytes) -> bytes:
        """
        Ожидание нужного ответа
        :param expected: ответ, который мы ожидаем
        :return: Ответ от каретки
        :raises: MoveResponseException - если ошибка при ожидании ответа
        """
        try:
            logger.debug("Waiting for response. Expected: %s", expected)
            response = self.client.read_until(
                expected=bytes(expected)
            )
            logger.debug("Received response: %s", response)
        except Exception as exception:
            logger.exception("Exception occurred while waiting for response",
                             exc_info=exception)
            raise MoveResponseException from exception
        return response

    async def __send_request(self, request: list) -> None:
        """
        Отправка сигнала на каретку
        :param request: Запрос (массив байт)
        :return:
        :raises: MoveRequestException - если вышел таймаут
        """
        try:
            logger.debug("Sending request: %s", request)
            self.client.write(request)
        except SerialTimeoutException as exception:
            logger.error("Error occurred while trying to send request: %s", exception.strerror)
            raise MoveRequestException from exception
