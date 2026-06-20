from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_user
from app.repositories.faculty import faculty_repo
from app.repositories.rooms import room_repo
from app.schemes.rooms import RoomCreate, RoomRead, RoomUpdate

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
    dependencies=[Depends(get_current_user)],
)


async def _ensure_faculty_exists(session: SessionDep, faculty_id: int) -> None:
    if await faculty_repo.get(session, faculty_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faculty {faculty_id} does not exist",
        )


@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(payload: RoomCreate, session: SessionDep) -> RoomRead:
    await _ensure_faculty_exists(session, payload.faculty_id)
    return await room_repo.create(session, payload)


@router.get("/", response_model=list[RoomRead])
async def list_rooms(session: SessionDep, skip: int = 0, limit: int = 100):
    return await room_repo.get_all(session, skip=skip, limit=limit)


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: int, session: SessionDep) -> RoomRead:
    room = await room_repo.get(session, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.patch("/{room_id}", response_model=RoomRead)
async def update_room(room_id: int, payload: RoomUpdate, session: SessionDep) -> RoomRead:
    if payload.faculty_id is not None:
        await _ensure_faculty_exists(session, payload.faculty_id)
    room = await room_repo.update(session, room_id, payload)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, session: SessionDep) -> None:
    deleted = await room_repo.delete(session, room_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
