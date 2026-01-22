from aiogram.fsm.state import State, StatesGroup


class GetManga(StatesGroup):
    waiting_for_title = State()