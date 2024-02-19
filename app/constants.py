from enum import Enum


LOGGING_FORMAT = "%(levelname)s %(name)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s"
LOGGING_DATETIME = "%Y-%m-%d %H:%M:%S"

MOVE_RESPONSE_BYTES = 8


class LidarMessages(Enum):
    """
    Сообщения для общения с лидаром
    """
    MESSAGE_LOGIN_CLIENT = (b'\x02\x02\x02\x02\x00\x00\x00\x17\x73\x4D\x4E\x20\x53\x65\x74\x41\x63\x63\x65\x73\x73\x4D'
                            b'\x6F\x64\x65\x20\x03\xF4\x72\x47\x44\xB3')
    MESSAGE_LOGIN_SERVICE = (b'\x02\x02\x02\x02\x00\x00\x00\x17\x73\x4D\x4E\x20\x53\x65\x74\x41\x63\x63\x65\x73\x73'
                             b'\x4D\x6F\x64\x65\x20\x04\x81\xBE\x23\xAA\x87')
    MESSAGE_CONFIGURE_5 = (b'\x02\x02\x02\x02\x00\x00\x00\x20\x73\x57\x4E\x20\x4C\x4D\x44\x73\x63\x61\x6E\x64\x61\x74'
                           b'\x61\x63\x66\x67\x20\x01\x00\x02\x01\x01\x01\x00\x00\x00\x00\x00\x00\x05\x45')
    MESSAGE_LOGOUT = b'\x02\x02\x02\x02\x00\x00\x00\x07\x73\x4D\x4E\x20\x52\x75\x6E\x19'
    MESSAGE_START_MES = (b'\x02\x02\x02\x02\x00\x00\x00\x10\x73\x4D\x4E\x20\x4C\x4D\x43\x73\x74\x61\x72\x74\x6D\x65'
                         b'\x61\x73\x68')
    MESSAGE_STANDBY = b'\x02\x02\x02\x02\x00\x00\x00\x0E\x73\x4D\x4E\x20\x4C\x4D\x43\x73\x74\x61\x6E\x64\x62\x79\x65'


class MoveStages(Enum):
    """
    Этапы движения каретки
    """
    STARTED = "CARRIAGE_STARTED"
    MOVED = "CARRIAGE_MOVED"
    STOPPED = "CARRIAGE_STOPPED"
    RETURNED = "CARRIAGE_RETURNED"


class Move(Enum):
    """
    Команды для управления кареткой
        0x00, 0x00, 0x02 - протокол общения
        0x01 - стоп
        0x02 - исходное
        0x03 - старт
        2 байта - контрольная сумма
    """
    START = [0x00, 0x00, 0x02, 0x03, 0x45, 0x41]
    STOP = [0x00, 0x00, 0x02, 0x01, 0x84, 0xc0]
    RETURN = [0x00, 0x00, 0x02, 0x02, 0x85, 0x80]


class MoveResponsesDevice1(Enum):
    """
    Ответы от первой каретки (автоматически возвращаются при выполнении
        соответствующих команд)
    """
    MOVE_COMPLETED = [0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x1E, 0xFC]
    STOP = [0x01, 0x01, 0x03, 0x00, 0x01, 0x00, 0xDE, 0x3D]


class MoveResponsesDevice2(Enum):
    """
    Ответы от второй каретки (необходимо делать
        запрос к каретке для получения ответа)
    """
    REQUEST = [0x01, 0x02, 0x03, 0x00, 0xE8, 0xA0]
    MOVE_COMPLETED = [0x01, 0x02, 0x03, 0x00, 0x01, 0x01, 0x1E, 0xB8]
    STOP = [0x01, 0x02, 0x03, 0x00, 0x01, 0x00, 0xDE, 0x79]
    NOT_COMPLETED = [0x01, 0x02, 0x03, 0x00, 0x01, 0x02, 0x1F, 0xF8]


if __name__ == '__main__':
    pass
