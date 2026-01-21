from aiogram import Router

from ...core.service.message import TextGenerator


class CommandHandlers:
    def __init__(self, text_api: TextGenerator):
        self.text_api = text_api
        self.router = Router()

        self._setup_handlers()

    def _setup_handlers(self): ...
