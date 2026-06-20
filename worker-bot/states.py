from aiogram.fsm.state import State, StatesGroup


class WorkerAuthStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()
