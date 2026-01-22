"""Хранит ошибки, конфиги, типы."""

from ._config import config
from ._errors import ParserError, MissingRequiredAttributeError, FetchError, LoadError, SpiderError

from ._types import ReturnType, FindMethod

__all__ = [
    "config",
    "ParserError",
    "MissingRequiredAttributeError",
    "ReturnType",
    "FindMethod",
    "FetchError",
    "LoadError",
    "SpiderError"
]
