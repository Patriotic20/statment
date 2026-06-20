"""Extra seed script — appends an additional, independent block of test data.

Self-contained: creates its own faculties/rooms/employees/inventory/issues/
telegram-clients/workers with unique keys that don't collide with seed.py.
Safe to run after seed.py on a fresh DB. Re-running it twice will conflict on
the unique keys (faculty.name, jshir, username, telegram_id), so run once.
"""
import asyncio

import app.models  # noqa: F401 — register all models with Base
from app.core.db import async_session_maker
from app.core.security import hash_password
from app.models.employees import Employee
from app.models.faculty import Faculty
from app.models.inventory import Inventory
from app.models.issues import Issue, IssueStatus, IssueType
from app.models.rooms import Floor, Room
from app.models.statement import Statement
from app.models.telegram_clients import TelegramClient
from app.models.user import User


async def seed_extra() -> None:
    async with async_session_maker() as session:
        # ── Faculties ────────────────────────────────────────────────────────
        faculties = [
            Faculty(name="Медицинский факультет"),
            Faculty(name="Педагогический факультет"),
        ]
        session.add_all(faculties)
        await session.flush()

        med, ped = faculties

        # ── Rooms ────────────────────────────────────────────────────────────
        rooms = [
            Room(name="Кабинет 110", floor=Floor.FIRST, faculty_id=med.id),
            Room(name="Кабинет 210", floor=Floor.SECOND, faculty_id=med.id),
            Room(name="Кабинет 310", floor=Floor.THIRD, faculty_id=ped.id),
            Room(name="Кабинет 410", floor=Floor.FOURTH, faculty_id=ped.id),
        ]
        session.add_all(rooms)
        await session.flush()

        r110, r210, r310, r410 = rooms

        # ── Employees (jshir с префиксом 3..., чтобы не пересекаться с seed) ──
        employees = [
            Employee(jshir="30000000000001", full_name="Ибрагимов Тимур Анварович", room_id=r110.id),
            Employee(jshir="30000000000002", full_name="Садыкова Лола Рустамовна", room_id=r110.id),
            Employee(jshir="30000000000003", full_name="Усманов Бекзод Шавкатович", room_id=r210.id),
            Employee(jshir="30000000000004", full_name="Камилова Нигора Фарходовна", room_id=r310.id),
            Employee(jshir="30000000000005", full_name="Тошматов Улугбек Зафарович", room_id=r410.id),
            Employee(jshir="30000000000006", full_name="Расулова Севара Дилшодовна", room_id=r410.id),
        ]
        session.add_all(employees)
        await session.flush()

        e1, e2, e3, e4, e5, e6 = employees

        # ── Inventory (коды INV-101+) ────────────────────────────────────────
        inventory = [
            Inventory(name="HP ProDesk 400 G7", code="INV-101", ip_address="192.168.5.10", device_type=IssueType.COMPUTER, employee_id=e1.id),
            Inventory(name="Brother HL-L2370DW", code="INV-102", ip_address=None, device_type=IssueType.PRINTER, employee_id=e1.id),
            Inventory(name="Dell Vostro 3710", code="INV-103", ip_address="192.168.5.11", device_type=IssueType.COMPUTER, employee_id=e2.id),
            Inventory(name="MikroTik hEX S Router", code="INV-104", ip_address="192.168.5.1", device_type=IssueType.NETWORK, employee_id=e3.id),
            Inventory(name="Lenovo V50t", code="INV-105", ip_address="192.168.6.10", device_type=IssueType.COMPUTER, employee_id=e4.id),
            Inventory(name="Xerox B210", code="INV-106", ip_address=None, device_type=IssueType.PRINTER, employee_id=e5.id),
            Inventory(name="TP-Link TL-SG1016D Switch", code="INV-107", ip_address="192.168.6.1", device_type=IssueType.NETWORK, employee_id=e6.id),
        ]
        session.add_all(inventory)
        await session.flush()

        # ── Issues (telegram_id с префиксом 2..., чтобы не пересекаться) ─────
        issues = [
            Issue(issue_type=IssueType.COMPUTER, status=IssueStatus.NEW, employee_id=e1.id, telegram_id=200000001),
            Issue(issue_type=IssueType.PRINTER, status=IssueStatus.IN_PROGRESS, employee_id=e1.id, telegram_id=200000001),
            Issue(issue_type=IssueType.NETWORK, status=IssueStatus.NEW, employee_id=e3.id, telegram_id=200000003),
            Issue(issue_type=IssueType.COMPUTER, status=IssueStatus.RESOLVED, employee_id=e4.id, telegram_id=200000004),
            Issue(issue_type=IssueType.NETWORK, status=IssueStatus.IN_PROGRESS, employee_id=e6.id, telegram_id=200000006),
        ]
        session.add_all(issues)
        await session.flush()

        # ── Telegram clients (telegram_id 200000001+) ────────────────────────
        telegram_clients = [
            TelegramClient(telegram_id=200000001, employee_id=e1.id, telegram_username="t_ibragimov", telegram_first_name="Тимур"),
            TelegramClient(telegram_id=200000003, employee_id=e3.id, telegram_username="b_usmanov", telegram_first_name="Бекзод"),
            TelegramClient(telegram_id=200000004, employee_id=e4.id, telegram_username=None, telegram_first_name="Нигора"),
            TelegramClient(telegram_id=200000006, employee_id=e6.id, telegram_username="s_rasulova", telegram_first_name="Севара"),
        ]
        session.add_all(telegram_clients)

        # ── Workers (с факультетами, чтобы сразу тестировать уведомления) ─────
        users = [
            User(username="worker_med", password=hash_password("worker123"), faculty_id=med.id),
            User(username="worker_ped", password=hash_password("worker123"), faculty_id=ped.id),
            User(username="worker_extra", password=hash_password("worker123")),  # без факультета — для текста «не назначен»
        ]
        session.add_all(users)
        await session.flush()

        worker_med, worker_ped, _ = users

        # ── Statements ───────────────────────────────────────────────────────
        statements = [
            Statement(description="Не загружается ОС после сбоя питания", user_id=worker_med.id, room_id=r110.id, employee_id=e1.id),
            Statement(description="Принтер выдаёт ошибку драйвера", user_id=worker_med.id, room_id=r210.id, employee_id=e3.id),
            Statement(description="Пропадает сеть в кабинете 410", user_id=worker_ped.id, room_id=r410.id, employee_id=e6.id),
        ]
        session.add_all(statements)

        await session.commit()
        print("✓ Extra faculties:       ", len(faculties))
        print("✓ Extra rooms:           ", len(rooms))
        print("✓ Extra employees:       ", len(employees))
        print("✓ Extra inventory:       ", len(inventory))
        print("✓ Extra issues:          ", len(issues))
        print("✓ Extra telegram clients:", len(telegram_clients))
        print("✓ Extra workers:         ", len(users))
        print("✓ Extra statements:      ", len(statements))
        print("\nNew worker logins:")
        print("  worker_med   / worker123  (Медицинский)")
        print("  worker_ped   / worker123  (Педагогический)")
        print("  worker_extra / worker123  (без факультета)")


if __name__ == "__main__":
    asyncio.run(seed_extra())
