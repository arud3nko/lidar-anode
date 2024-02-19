class MoveException(Exception):
    """
    Исключение, выпадающее в случае ошибки во время движения каретки
    """
    pass


class MoveRequestException(Exception):
    """
    Исключение, выпадающее в случае ошибки передачи команды на каретку
    """
    pass


class MoveResponseException(Exception):
    """
    Исключение, выпадающее в случае ошибки приёма ответа от каретки
    """
    pass
