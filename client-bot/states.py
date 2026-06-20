from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    """Состояния аутентификации клиента по ЖШИР."""
    waiting_for_jshir = State()
