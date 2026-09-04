from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_user
from app.core.errors import unique_violation_as_400
from app.repositories.employees import employee_repo
from app.repositories.rooms import room_repo
from app.schemes.employees import EmployeeCreate, EmployeeRead, EmployeeUpdate

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)],
)

# Сообщения для нарушений уникальности (имена constraint'ов в PostgreSQL).
_UNIQUE_MESSAGES = {"employees_jshir_key": "Bunday JShShIR bilan xodim allaqachon mavjud"}


async def _ensure_room_exists(session: SessionDep, room_id: int) -> None:
    if await room_repo.get(session, room_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Xona {room_id} mavjud emas",
        )


@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, session: SessionDep) -> EmployeeRead:
    await _ensure_room_exists(session, payload.room_id)
    async with unique_violation_as_400(_UNIQUE_MESSAGES, "Xodimni yaratib bo'lmadi"):
        return await employee_repo.create(session, payload)


@router.get("/", response_model=list[EmployeeRead])
async def list_employees(
    session: SessionDep,
    room_id: int | None = None,
    faculty_id: int | None = None,
    jshir: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    if jshir is not None:
        employee = await employee_repo.get_by_jshir(session, "".join(jshir.split()))
        return [employee] if employee is not None else []
    if room_id is not None:
        return await employee_repo.get_by_room(session, room_id, skip=skip, limit=limit)
    if faculty_id is not None:
        return await employee_repo.get_by_faculty(session, faculty_id, skip=skip, limit=limit)
    return await employee_repo.get_all(session, skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: int, session: SessionDep) -> EmployeeRead:
    employee = await employee_repo.get(session, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xodim topilmadi")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: int, payload: EmployeeUpdate, session: SessionDep
) -> EmployeeRead:
    if payload.room_id is not None:
        await _ensure_room_exists(session, payload.room_id)
    async with unique_violation_as_400(_UNIQUE_MESSAGES, "Xodimni yangilab bo'lmadi"):
        employee = await employee_repo.update(session, employee_id, payload)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xodim topilmadi")
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, session: SessionDep) -> None:
    deleted = await employee_repo.delete(session, employee_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xodim topilmadi")
