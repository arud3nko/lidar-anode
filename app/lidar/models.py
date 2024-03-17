"""

В этом модуле реализованы модели pydantic

"""
from typing_extensions import Annotated

from pydantic import BaseModel, StrictFloat, StrictInt, Field


class LidarParams(BaseModel):
    """

    Этот класс описывает параметры лидара

    """
    ip:      str
    port:    Annotated[StrictInt, Field(gt=0)]
    timeout: Annotated[StrictFloat, Field(ge=0)] = 0
