from sqlalchemy.orm import sessionmaker

from app.core.logging import get_logger
from app.models import Camera
from app.services.detector import PlateDetector
from app.services.frame_store import LatestFrameStore
from app.services.ocr import PlateOCR
from app.services.realtime import RealtimeBroker
from app.workers.stream_worker import StreamWorker

logger = get_logger(__name__)


class CameraManager:
    def __init__(self, session_factory: sessionmaker, broker: RealtimeBroker) -> None:
        self.session_factory = session_factory
        self.broker = broker
        self.detector = PlateDetector()
        self.ocr = PlateOCR()
        self.frames = LatestFrameStore()
        self.workers: dict[int, StreamWorker] = {}

    async def start_all_enabled(self) -> None:
        with self.session_factory() as db:
            cameras = db.query(Camera).filter(Camera.enabled.is_(True)).all()
            for camera in cameras:
                await self.start_camera(camera.id)

    async def start_camera(self, camera_id: int) -> None:
        if camera_id in self.workers:
            return
        with self.session_factory() as db:
            camera = db.get(Camera, camera_id)
            if not camera or not camera.enabled:
                return
            worker = StreamWorker(camera, self.session_factory, self.broker, self.detector, self.ocr, self.frames)
            worker.start()
            self.workers[camera_id] = worker
            logger.info("Started camera worker %s", camera_id)

    async def stop_camera(self, camera_id: int) -> None:
        worker = self.workers.pop(camera_id, None)
        if worker:
            await worker.stop()
            await self.frames.remove(camera_id)
            logger.info("Stopped camera worker %s", camera_id)

    async def restart_camera(self, camera_id: int) -> None:
        await self.stop_camera(camera_id)
        await self.start_camera(camera_id)

    async def stop_all(self) -> None:
        for camera_id in list(self.workers):
            await self.stop_camera(camera_id)
