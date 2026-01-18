class ParserError(Exception):
    """Базовый класс исключений парсера."""

class MissingRequiredAttributeError(ParserError):
    """Исключение, возникающее при отсутствии обязательного атрибута при парсинге."""
    
