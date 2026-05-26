import asyncio
import time

import cv2
import numpy as np


class LatestFrameStore:
    def __init__(self) -> None:
        self._frames: dict[int, tuple[bytes, float]] = {}
        self._lock = asyncio.Lock()
        self._placeholder = self._make_placeholder()

    async def update(self, camera_id: int, frame: np.ndarray) -> None:
        ok, encoded = await asyncio.to_thread(cv2.imencode, ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 78])
        if not ok:
            return
        async with self._lock:
            self._frames[camera_id] = (encoded.tobytes(), time.time())

    async def get(self, camera_id: int) -> bytes | None:
        async with self._lock:
            item = self._frames.get(camera_id)
            return item[0] if item else None

    async def get_or_placeholder(self, camera_id: int) -> bytes:
        frame = await self.get(camera_id)
        return frame or self._placeholder

    async def remove(self, camera_id: int) -> None:
        async with self._lock:
            self._frames.pop(camera_id, None)

    @staticmethod
    def _make_placeholder() -> bytes:
        image = np.zeros((360, 640, 3), dtype=np.uint8)
        image[:] = (18, 24, 30)
        cv2.putText(
            image,
            "Waiting for camera frames",
            (150, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (180, 190, 200),
            2,
            cv2.LINE_AA,
        )
        ok, encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 78])
        return encoded.tobytes() if ok else b""
