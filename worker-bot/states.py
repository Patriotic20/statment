from aiogram.fsm.state import State, StatesGroup


class WorkerAuthStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()


class RoomStates(StatesGroup):
    """Мастер добавления кабинета: название → этаж → факультет."""
    waiting_name = State()
    waiting_floor = State()
    waiting_faculty = State()


class EmployeeStates(StatesGroup):
    """Мастер добавления сотрудника: ЖШИР → ФИО → факультет → кабинет."""
    waiting_jshir = State()
    waiting_full_name = State()
    waiting_faculty = State()
    waiting_room = State()


class InventoryStates(StatesGroup):
    """Мастер добавления оборудования.

    Владелец обязателен (inventory.employee_id NOT NULL), поэтому сотрудник
    выбирается внутри мастера — с возможностью создать нового по ходу дела.
    """
    waiting_name = State()
    waiting_device_type = State()
    waiting_photo = State()
    waiting_ip = State()
    waiting_mac = State()
    waiting_faculty = State()
    waiting_room = State()
    waiting_employee = State()


class AssignStates(StatesGroup):
    """Назначение существующего оборудования другому сотруднику."""
    waiting_faculty = State()
    waiting_room = State()
    waiting_item = State()
    waiting_employee = State()
