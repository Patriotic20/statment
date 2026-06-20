from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_user
from app.repositories.faculty import faculty_repo
from app.schemes.faculty import FacultyCreate, FacultyRead, FacultyUpdate

router = APIRouter(prefix="/faculties", tags=["faculties"])


@router.post("/", response_model=FacultyRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_user)])
async def create_faculty(payload: FacultyCreate, session: SessionDep) -> FacultyRead:
    return await faculty_repo.create(session, payload)


@router.get("/", response_model=list[FacultyRead])
async def list_faculties(session: SessionDep, skip: int = 0, limit: int = 100):
    return await faculty_repo.get_all(session, skip=skip, limit=limit)


@router.get("/{faculty_id}", response_model=FacultyRead)
async def get_faculty(faculty_id: int, session: SessionDep) -> FacultyRead:
    faculty = await faculty_repo.get(session, faculty_id)
    if faculty is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    return faculty


@router.patch("/{faculty_id}", response_model=FacultyRead,
              dependencies=[Depends(get_current_user)])
async def update_faculty(
    faculty_id: int, payload: FacultyUpdate, session: SessionDep
) -> FacultyRead:
    faculty = await faculty_repo.update(session, faculty_id, payload)
    if faculty is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
    return faculty


@router.delete("/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_user)])
async def delete_faculty(faculty_id: int, session: SessionDep) -> None:
    deleted = await faculty_repo.delete(session, faculty_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
