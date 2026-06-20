from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Import models so SQLAlchemy metadata is fully populated.
import app.models  # noqa: F401
from app.routers import auth, employees, faculty, inventory, issues, rooms, telegram, users
from app.rabbitmq import rabbitmq_manager
from app.websocket import manager as ws_manager
from app.core.security import decode_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_manager.connect()
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
