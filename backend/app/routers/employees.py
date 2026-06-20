from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_user
from app.repositories.employees import employee_repo
from app.repositories.rooms import room_repo
from app.schemes.employees import EmployeeCreate, EmployeeRead, EmployeeUpdate

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)],
)


async def _ensure_room_exists(session: SessionDep, room_id: int) -> None:
    if await room_repo.get(session, room_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room {room_id} does not exist",
        )


@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, session: SessionDep) -> EmployeeRead:
    await _ensure_room_exists(session, payload.room_id)
    return await employee_repo.create(session, payload)


@router.get("/", response_model=list[EmployeeRead])
async def list_employees(session: SessionDep, skip: int = 0, limit: int = 100):
    return await employee_repo.get_all(session, skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: int, session: SessionDep) -> EmployeeRead:
    employee = await employee_repo.get(session, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: int, payload: EmployeeUpdate, session: SessionDep
) -> EmployeeRead:
    if payload.room_id is not None:
        await _ensure_room_exists(session, payload.room_id)
    employee = await employee_repo.update(session, employee_id, payload)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, session: SessionDep) -> None:
    deleted = await employee_repo.delete(session, employee_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
