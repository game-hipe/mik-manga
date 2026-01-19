"""Хранит ошибки, конфиги, типы."""

from ._config import config
from ._errors import ParserError, MissingRequiredAttributeError, FetchError

from ._types import ReturnType, FindMethod

__all__ = [
    "FUCKWORLD",
    "config",
    "ParserError",
    "MissingRequiredAttributeError",
    "ReturnType",
    "FindMethod",
    "FetchError",
]
