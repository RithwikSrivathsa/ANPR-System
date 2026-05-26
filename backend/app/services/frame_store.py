import asyncio
import time

import cv2
import numpy as np


class LatestFrameStore:
    def __init__(self) -> None:
        self._frames: dict[int, tuple[bytes, float]] = {}
        self._lock = asyncio.Lock()

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

    async def remove(self, camera_id: int) -> None:
        async with self._lock:
            self._frames.pop(camera_id, None)
