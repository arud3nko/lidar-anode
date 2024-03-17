from enum import Enum


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