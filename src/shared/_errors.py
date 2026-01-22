class ParserError(Exception):
    """Базовый класс исключений парсера."""


class MissingRequiredAttributeError(ParserError):
    """Исключение, возникающее при отсутствии обязательного атрибута при парсинге."""


class FetchError(Exception):
    """Исключение, возникающее при ошибке при запросе."""

class LoadError(Exception):
    """Исключение, возникающее при ошибке при загрузке."""
    
class SpiderError(LoadError):
    """Исключение, возникающее при ошибке в работе паука."""