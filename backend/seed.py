"""Seed script — fills the database with test data."""
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


async def seed() -> None:
    async with async_session_maker() as session:
        # ── Faculties ────────────────────────────────────────────────────────
        faculties = [
            Faculty(name="Факультет информационных технологий"),
            Faculty(name="Факультет экономики и управления"),
            Faculty(name="Юридический факультет"),
            Faculty(name="Факультет иностранных языков"),
        ]
        session.add_all(faculties)
        await session.flush()

        fit, feu, law, lang = faculties

        # ── Rooms ────────────────────────────────────────────────────────────
        rooms = [
            Room(name="Кабинет 101", floor=Floor.FIRST, faculty_id=fit.id),
            Room(name="Кабинет 102", floor=Floor.FIRST, faculty_id=fit.id),
            Room(name="Кабинет 103", floor=Floor.FIRST, faculty_id=fit.id),
            Room(name="Кабинет 201", floor=Floor.SECOND, faculty_id=feu.id),
            Room(name="Кабинет 202", floor=Floor.SECOND, faculty_id=feu.id),
            Room(name="Кабинет 301", floor=Floor.THIRD, faculty_id=law.id),
            Room(name="Кабинет 302", floor=Floor.THIRD, faculty_id=law.id),
            Room(name="Кабинет 401", floor=Floor.FOURTH, faculty_id=lang.id),
        ]
        session.add_all(rooms)
        await session.flush()

        r101, r102, r103, r201, r202, r301, r302, r401 = rooms

        # ── Employees ────────────────────────────────────────────────────────
        employees = [
            Employee(jshir="12345678901234", full_name="Алиев Бахтиёр Рустамович", room_id=r101.id),
            Employee(jshir="23456789012345", full_name="Каримова Дилноза Юсуповна", room_id=r101.id),
            Employee(jshir="34567890123456", full_name="Рашидов Отабек Нормуродович", room_id=r102.id),
            Employee(jshir="45678901234567", full_name="Хасанова Малика Азизовна", room_id=r201.id),
            Employee(jshir="56789012345678", full_name="Юсупов Санжар Холматович", room_id=r201.id),
            Employee(jshir="67890123456789", full_name="Назаров Фирдавс Ибрагимович", room_id=r202.id),
            Employee(jshir="78901234567890", full_name="Турсунов Жасур Баходирович", room_id=r301.id),
            Employee(jshir="89012345678901", full_name="Эргашева Нилуфар Алишеровна", room_id=r302.id),
            Employee(jshir="90123456789012", full_name="Собиров Акмал Фарходович", room_id=r103.id),
            Employee(jshir="01234567890123", full_name="Мирзаева Зухра Бахтияровна", room_id=r401.id),
        ]
        session.add_all(employees)
        await session.flush()

        emp1, emp2, emp3, emp4, emp5, emp6, emp7, emp8, emp9, emp10 = employees

        # ── Inventory ────────────────────────────────────────────────────────
        inventory = [
            Inventory(name="Dell Optiplex 7090", code="INV-001", ip_address="192.168.1.10", device_type=IssueType.COMPUTER, employee_id=emp1.id),
            Inventory(name="HP LaserJet Pro M404dn", code="INV-002", ip_address="192.168.1.11", device_type=IssueType.PRINTER, employee_id=emp1.id),
            Inventory(name="Lenovo ThinkCentre M720", code="INV-003", ip_address="192.168.1.20", device_type=IssueType.COMPUTER, employee_id=emp2.id),
            Inventory(name="Canon imageCLASS MF445dw", code="INV-004", ip_address=None, device_type=IssueType.PRINTER, employee_id=emp3.id),
            Inventory(name="HP EliteDesk 800 G6", code="INV-005", ip_address="192.168.2.10", device_type=IssueType.COMPUTER, employee_id=emp4.id),
            Inventory(name="Cisco SG350-28 Switch", code="INV-006", ip_address="192.168.2.1", device_type=IssueType.NETWORK, employee_id=emp5.id),
            Inventory(name="ASUS ExpertCenter D700MC", code="INV-007", ip_address="192.168.3.10", device_type=IssueType.COMPUTER, employee_id=emp7.id),
            Inventory(name="Epson EcoTank L3250", code="INV-008", ip_address=None, device_type=IssueType.PRINTER, employee_id=emp8.id),
            Inventory(name="Acer Veriton X2690G", code="INV-009", ip_address="192.168.1.30", device_type=IssueType.COMPUTER, employee_id=emp9.id),
            Inventory(name="TP-Link Archer C80 Router", code="INV-010", ip_address="192.168.4.1", device_type=IssueType.NETWORK, employee_id=emp10.id),
        ]
        session.add_all(inventory)
        await session.flush()

        # ── Issues ───────────────────────────────────────────────────────────
        issues = [
            Issue(issue_type=IssueType.COMPUTER, status=IssueStatus.NEW, employee_id=emp1.id, telegram_id=100000001),
            Issue(issue_type=IssueType.PRINTER, status=IssueStatus.IN_PROGRESS, employee_id=emp2.id, telegram_id=100000002),
            Issue(issue_type=IssueType.NETWORK, status=IssueStatus.RESOLVED, employee_id=emp3.id, telegram_id=100000003),
            Issue(issue_type=IssueType.COMPUTER, status=IssueStatus.NEW, employee_id=emp4.id, telegram_id=100000004),
            Issue(issue_type=IssueType.NETWORK, status=IssueStatus.IN_PROGRESS, employee_id=emp5.id, telegram_id=100000005),
            Issue(issue_type=IssueType.PRINTER, status=IssueStatus.NEW, employee_id=emp7.id, telegram_id=100000007),
            Issue(issue_type=IssueType.COMPUTER, status=IssueStatus.RESOLVED, employee_id=emp8.id, telegram_id=100000008),
            Issue(issue_type=IssueType.NETWORK, status=IssueStatus.NEW, employee_id=emp9.id, telegram_id=100000009),
            Issue(issue_type=IssueType.PRINTER, status=IssueStatus.IN_PROGRESS, employee_id=emp10.id, telegram_id=100000010),
        ]
        session.add_all(issues)
        await session.flush()

        # ── Users ────────────────────────────────────────────────────────────
        users = [
            User(username="admin", password=hash_password("admin123"), faculty_id=fit.id),
            User(username="worker_fit", password=hash_password("worker123"), faculty_id=fit.id),
            User(username="worker_feu", password=hash_password("worker123"), faculty_id=feu.id),
            User(username="worker_law", password=hash_password("worker123"), faculty_id=law.id),
            User(username="worker_lang", password=hash_password("worker123"), faculty_id=lang.id),
        ]
        session.add_all(users)
        await session.flush()

        admin, worker_fit, worker_feu, worker_law, worker_lang = users

        # ── Telegram clients ─────────────────────────────────────────────────
        telegram_clients = [
            TelegramClient(telegram_id=100000001, employee_id=emp1.id, telegram_username="b_aliev", telegram_first_name="Бахтиёр"),
            TelegramClient(telegram_id=100000002, employee_id=emp2.id, telegram_username="d_karimova", telegram_first_name="Дилноза"),
            TelegramClient(telegram_id=100000003, employee_id=emp3.id, telegram_username="o_rashidov", telegram_first_name="Отабек"),
            TelegramClient(telegram_id=100000005, employee_id=emp5.id, telegram_username=None, telegram_first_name="Санжар"),
            TelegramClient(telegram_id=100000008, employee_id=emp8.id, telegram_username="n_ergasheva", telegram_first_name="Нилуфар"),
        ]
        session.add_all(telegram_clients)

        # ── Statements ───────────────────────────────────────────────────────
        statements = [
            Statement(description="Не включается компьютер после обновления", user_id=worker_fit.id, room_id=r101.id, employee_id=emp1.id),
            Statement(description="Принтер не печатает, замятие бумаги", user_id=worker_fit.id, room_id=r101.id, employee_id=emp2.id),
            Statement(description="Нет доступа к локальной сети", user_id=worker_feu.id, room_id=r201.id, employee_id=emp4.id),
            Statement(description="Требуется замена картриджа", user_id=worker_law.id, room_id=r301.id, employee_id=emp7.id),
            Statement(description="Медленная работа сети в кабинете", user_id=worker_lang.id, room_id=r401.id, employee_id=emp10.id),
        ]
        session.add_all(statements)

        await session.commit()
        print("✓ Faculties:       ", len(faculties))
        print("✓ Rooms:           ", len(rooms))
        print("✓ Employees:       ", len(employees))
        print("✓ Inventory:       ", len(inventory))
        print("✓ Issues:          ", len(issues))
        print("✓ Users:           ", len(users))
        print("✓ Telegram clients:", len(telegram_clients))
        print("✓ Statements:      ", len(statements))
        print("\nLogins:")
        print("  admin       / admin123")
        print("  worker_fit  / worker123  (ФИТ)")
        print("  worker_feu  / worker123  (ФЭУ)")
        print("  worker_law  / worker123  (Юридический)")
        print("  worker_lang / worker123  (Иностранных языков)")


if __name__ == "__main__":
    asyncio.run(seed())
