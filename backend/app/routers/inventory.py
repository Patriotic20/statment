import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import SessionDep, get_current_user
from app.core.errors import unique_violation_as_400
from app.models.issues import IssueType
from app.repositories.employees import employee_repo
from app.repositories.inventory import inventory_repo
from app.schemes.inventory import InventoryCreate, InventoryRead, InventoryUpdate

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(get_current_user)],
)

_UNIQUE_MESSAGES = {
    "inventory_mac_address_key": "Bunday MAC-manzilli uskuna allaqachon ro'yxatdan o'tgan",
}

# Фотографии храним только в этих форматах: то, что реально присылает Telegram,
# плюс webp. Расширение берём отсюда же, а не из имени присланного файла.
_ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

_PHOTO_DIR = Path(settings.MEDIA_ROOT) / "inventory"


async def _ensure_employee_exists(session: SessionDep, employee_id: int) -> None:
    if await employee_repo.get(session, employee_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Xodim {employee_id} mavjud emas",
        )


@router.post("/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def create_inventory(payload: InventoryCreate, session: SessionDep) -> InventoryRead:
    await _ensure_employee_exists(session, payload.employee_id)
    async with unique_violation_as_400(_UNIQUE_MESSAGES, "Uskunani yaratib bo'lmadi"):
        return await inventory_repo.create(session, payload)


@router.get("/", response_model=list[InventoryRead])
async def list_inventory(
    session: SessionDep,
    employee_id: int | None = None,
    room_id: int | None = None,
    device_type: IssueType | None = None,
    skip: int = 0,
    limit: int = 100,
):
    if employee_id is None and room_id is None and device_type is None:
        return await inventory_repo.get_all(session, skip=skip, limit=limit)
    return await inventory_repo.get_filtered(
        session,
        employee_id=employee_id,
        room_id=room_id,
        device_type=device_type,
        skip=skip,
        limit=limit,
    )


@router.get("/{inventory_id}", response_model=InventoryRead)
async def get_inventory(inventory_id: int, session: SessionDep) -> InventoryRead:
    item = await inventory_repo.get(session, inventory_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uskuna topilmadi")
    return item


@router.post("/{inventory_id}/photo", response_model=InventoryRead)
async def upload_inventory_photo(
    inventory_id: int, session: SessionDep, file: UploadFile = File(...)
) -> InventoryRead:
    """Сохраняет фотографию устройства и записывает путь к ней в image_url."""
    item = await inventory_repo.get(session, inventory_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uskuna topilmadi")

    extension = _ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faqat JPEG, PNG yoki WebP formatidagi rasmlar qabul qilinadi",
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fayl hajmi {settings.MAX_UPLOAD_MB} MB dan oshmasligi kerak",
        )

    # Имя файла генерируем сами: присланному имени доверять нельзя.
    _PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    (_PHOTO_DIR / filename).write_bytes(content)

    updated = await inventory_repo.update(
        session, inventory_id, {"image_url": f"/media/inventory/{filename}"}
    )
    return updated


@router.patch("/{inventory_id}", response_model=InventoryRead)
async def update_inventory(
    inventory_id: int, payload: InventoryUpdate, session: SessionDep
) -> InventoryRead:
    if payload.employee_id is not None:
        await _ensure_employee_exists(session, payload.employee_id)
    async with unique_violation_as_400(_UNIQUE_MESSAGES, "Uskunani yangilab bo'lmadi"):
        item = await inventory_repo.update(session, inventory_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uskuna topilmadi")
    return item


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(inventory_id: int, session: SessionDep) -> None:
    deleted = await inventory_repo.delete(session, inventory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uskuna topilmadi")
