from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import analytics, auth, cameras, detections, health, logs, settings as settings_routes, websocket
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import Base, engine, SessionLocal
from app.services.camera_manager import CameraManager
from app.services.realtime import RealtimeBroker

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    broker = RealtimeBroker(settings.redis_url)
    manager = CameraManager(SessionLocal, broker)
    app.state.realtime = broker
    app.state.camera_manager = manager
    await broker.connect()
    await manager.start_all_enabled()
    logger.info("ANPR backend started")
    yield
    await manager.stop_all()
    await broker.close()
    logger.info("ANPR backend stopped")


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/snapshots", StaticFiles(directory=settings.snapshot_dir), name="snapshots")

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(detections.router, prefix="/detections", tags=["detections"])
app.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])
app.include_router(settings_routes.router, prefix="/settings", tags=["settings"])
app.include_router(websocket.router)
