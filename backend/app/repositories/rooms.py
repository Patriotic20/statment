from app.repositories.base import BaseRepository
from app.models.rooms import Room
from app.schemes.rooms import RoomCreate, RoomUpdate

class RoomRepository(BaseRepository[Room, RoomCreate, RoomUpdate]):
    def __init__(self):
        super().__init__(Room)

room_repo = RoomRepository()
