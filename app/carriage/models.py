"""

В этом модуле реализованы модели pydantic

"""
from typing_extensions import Annotated
from typing import Optional

from pydantic import BaseModel, StrictFloat, StrictInt, Field


class CarriageParams(BaseModel):
    """

    Этот класс описывает параметры каретки

    """
    port:     str
    baudrate: Annotated[StrictInt, Field(gt=0)] = 9600
    timeout:  Annotated[StrictFloat, Field(ge=0)] = 0
    move_time: Optional[Annotated[StrictFloat, Field(gt=0)]] = None
