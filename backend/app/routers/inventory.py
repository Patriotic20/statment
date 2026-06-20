from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_user
from app.repositories.employees import employee_repo
from app.repositories.inventory import inventory_repo
from app.schemes.inventory import InventoryCreate, InventoryRead, InventoryUpdate

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(get_current_user)],
)


async def _ensure_employee_exists(session: SessionDep, employee_id: int) -> None:
    if await employee_repo.get(session, employee_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee {employee_id} does not exist",
        )


@router.post("/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def create_inventory(payload: InventoryCreate, session: SessionDep) -> InventoryRead:
    await _ensure_employee_exists(session, payload.employee_id)
    return await inventory_repo.create(session, payload)


@router.get("/", response_model=list[InventoryRead])
async def list_inventory(session: SessionDep, skip: int = 0, limit: int = 100):
    return await inventory_repo.get_all(session, skip=skip, limit=limit)


@router.get("/{inventory_id}", response_model=InventoryRead)
async def get_inventory(inventory_id: int, session: SessionDep) -> InventoryRead:
    item = await inventory_repo.get(session, inventory_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return item


@router.patch("/{inventory_id}", response_model=InventoryRead)
async def update_inventory(
    inventory_id: int, payload: InventoryUpdate, session: SessionDep
) -> InventoryRead:
    if payload.employee_id is not None:
        await _ensure_employee_exists(session, payload.employee_id)
    item = await inventory_repo.update(session, inventory_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return item


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(inventory_id: int, session: SessionDep) -> None:
    deleted = await inventory_repo.delete(session, inventory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
