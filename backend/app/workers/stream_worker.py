import asyncio
import time
from datetime import datetime, timezone

import cv2
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.models import Camera, Detection, SystemLog
from app.services.dedupe import DuplicateSuppressor
from app.services.detector import PlateDetector
from app.services.frame_store import LatestFrameStore
from app.services.ocr import PlateOCR
from app.services.realtime import RealtimeBroker
from app.services.snapshot import save_snapshot
from app.services.tracker import SimpleByteTrackAdapter

logger = get_logger(__name__)


class StreamWorker:
    def __init__(
        self,
        camera: Camera,
        session_factory: sessionmaker,
        broker: RealtimeBroker,
        detector: PlateDetector,
        ocr: PlateOCR,
        frames: LatestFrameStore,
    ) -> None:
        self.camera_id = camera.id
        self.name = camera.name
        self.rtsp_url = camera.rtsp_url
        self.session_factory = session_factory
        self.broker = broker
        self.detector = detector
        self.ocr = ocr
        self.frames = frames
        self.tracker = SimpleByteTrackAdapter()
        self.dedupe = DuplicateSuppressor(settings.duplicate_timeout_seconds)
        self.stop_event = asyncio.Event()
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.task = asyncio.create_task(self.run(), name=f"camera-{self.camera_id}")

    async def stop(self) -> None:
        self.stop_event.set()
        if self.task:
            await asyncio.gather(self.task, return_exceptions=True)
        await self._log("info", "camera_worker_stopped")

    async def run(self) -> None:
        backoff = 1
        while not self.stop_event.is_set():
            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                await self._set_status("offline", "Unable to open RTSP stream")
                await self._log("warning", "camera_open_failed")
                await asyncio.sleep(min(backoff, 30))
                backoff *= 2
                continue
            await self._set_status("online", None)
            await self._log("info", "camera_stream_opened")
            backoff = 1
            frame_count = 0
            last_fps_at = time.time()
            processed = 0
            try:
                while not self.stop_event.is_set():
                    ok, frame = await asyncio.to_thread(cap.read)
                    if not ok or frame is None:
                        await self._set_status("reconnecting", "Frame read failed")
                        await self._log("warning", "camera_frame_read_failed")
                        break
                    frame_count += 1
                    if frame_count % settings.frame_skip != 0:
                        continue
                    processed += 1
                    await self._process_frame(frame, frame_count)
                    now = time.time()
                    if now - last_fps_at >= 5:
                        fps = processed / (now - last_fps_at)
                        await self._update_fps(fps)
                        await self.broker.publish({"type": "camera_status", "camera_id": self.camera_id, "fps": fps})
                        processed = 0
                        last_fps_at = now
            except Exception as exc:
                logger.exception("Camera %s crashed: %s", self.camera_id, exc)
                await self._set_status("error", str(exc))
            finally:
                cap.release()
            await asyncio.sleep(min(backoff, 30))
            backoff *= 2

    async def _process_frame(self, frame, frame_count: int) -> None:
        capture_started_at = datetime.now(timezone.utc)
        await self._log("info", f"frame_captured frame={frame_count} captured_at={capture_started_at.isoformat()}")
        self.dedupe.ttl_seconds = settings.duplicate_timeout_seconds
        candidates = await asyncio.to_thread(self.detector.detect, frame)
        preview = frame.copy()
        for candidate in candidates:
            x1, y1, x2, y2 = candidate.bbox
            cv2.rectangle(preview, (x1, y1), (x2, y2), (53, 240, 177), 2)
        await self.frames.update(self.camera_id, preview)
        if not candidates:
            await self._log("info", f"frame_processed frame={frame_count} candidates=0")
            return
        track_ids = self.tracker.update([candidate.bbox for candidate in candidates], frame)
        for candidate, track_id in zip(candidates, track_ids, strict=False):
            plate_text, ocr_conf = await asyncio.to_thread(self.ocr.read, candidate.crop)
            if not plate_text:
                await self._log("info", f"ocr_rejected frame={frame_count} track_id={track_id} confidence={ocr_conf:.3f}")
                continue
            if not self.dedupe.should_emit(self.camera_id, plate_text):
                await self._log("info", f"duplicate_removed plate={plate_text} track_id={track_id}")
                continue
            confidence = round((candidate.confidence + ocr_conf) / 2, 4)
            snapshot_path = await asyncio.to_thread(save_snapshot, self.camera_id, plate_text, candidate.crop)
            bbox = ",".join(str(v) for v in candidate.bbox)
            with self.session_factory() as db:
                detection = Detection(
                    plate_text=plate_text,
                    confidence=confidence,
                    camera_id=self.camera_id,
                    snapshot_path=snapshot_path,
                    track_id=track_id,
                    bbox=bbox,
                    detected_at=datetime.now(timezone.utc),
                )
                db.add(detection)
                db.add(
                    SystemLog(
                        level="info",
                        message=f"detection_saved plate={plate_text} snapshot={snapshot_path}",
                        camera_id=self.camera_id,
                    )
                )
                db.commit()
                db.refresh(detection)
                event = {
                    "type": "detection",
                    "id": detection.id,
                    "plate_text": detection.plate_text,
                    "confidence": detection.confidence,
                    "camera_id": self.camera_id,
                    "camera_name": self.name,
                    "snapshot_path": detection.snapshot_path,
                    "detected_at": detection.detected_at.isoformat(),
                    "track_id": detection.track_id,
                    "bbox": detection.bbox,
                }
            await self.broker.publish(event)
            await self._log(
                "info",
                f"frame_processed frame={frame_count} plate={plate_text} track_id={track_id} confidence={confidence}",
            )

    async def _set_status(self, status: str, error: str | None) -> None:
        with self.session_factory() as db:
            camera = db.get(Camera, self.camera_id)
            if camera:
                camera.status = status
                camera.last_error = error
            if error:
                db.add(SystemLog(level="warning", message=error, camera_id=self.camera_id))
            db.commit()
        await self.broker.publish({"type": "camera_status", "camera_id": self.camera_id, "status": status, "error": error})

    async def _update_fps(self, fps: float) -> None:
        with self.session_factory() as db:
            camera = db.get(Camera, self.camera_id)
            if camera:
                camera.fps = round(fps, 2)
                db.commit()

    async def _log(self, level: str, message: str) -> None:
        with self.session_factory() as db:
            db.add(SystemLog(level=level, message=message, camera_id=self.camera_id))
            db.commit()
