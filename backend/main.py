import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Import models so SQLAlchemy metadata is fully populated.
import app.models  # noqa: F401
from app.core.config import settings
from app.core.db import async_session_maker
from app.repositories.user import user_repo
from app.routers import auth, employees, faculty, inventory, issues, rooms, telegram, users
from app.rabbitmq import rabbitmq_manager
from app.websocket import manager as ws_manager
from app.core.security import decode_token

logger = logging.getLogger("uvicorn.error")


async def _ensure_admin() -> None:
    """Создаёт администратора из настроек (backend/.env), если его ещё нет."""
    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        logger.warning("ADMIN_USERNAME/ADMIN_PASSWORD не заданы — админ не создан")
        return
    async with async_session_maker() as session:
        existing = await user_repo.get_by_username(session, settings.ADMIN_USERNAME)
        if existing is not None:
            logger.info("Админ '%s' уже существует", settings.ADMIN_USERNAME)
            return
        # user_repo.create сам хеширует пароль.
        await user_repo.create(
            session,
            {"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD},
        )
        logger.info("Создан администратор '%s'", settings.ADMIN_USERNAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_manager.connect()
    try:
        await _ensure_admin()
    except Exception as exc:  # не валим старт приложения из-за этого
        logger.error("Не удалось создать администратора: %s", exc)
    yield
    await rabbitmq_manager.close()


app = FastAPI(title="RRTM API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(faculty.router)
app.include_router(rooms.router)
app.include_router(employees.router)
app.include_router(inventory.router)
app.include_router(telegram.router)
app.include_router(issues.router)
app.include_router(users.router)


@app.websocket("/ws/issues")
async def ws_issues(websocket: WebSocket, token: str | None = None):
    try:
        if not token:
            await websocket.close(code=1008)
            return
        decode_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
