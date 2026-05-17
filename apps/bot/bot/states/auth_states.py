"""FSM holatlari — login flow uchun."""
from aiogram.fsm.state import State, StatesGroup


class LoginStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()
