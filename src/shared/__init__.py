"""Хранит ошибки, конфиги, типы."""

from ._config import config
from ._errors import (
    ParserError,
    MissingRequiredAttributeError
)

from ._types import (
    ReturnType
)

__all__ = [
    'FUCKWORLD',
    'config',
    'ParserError',
    'MissingRequiredAttributeError',
    'ReturnType'
]