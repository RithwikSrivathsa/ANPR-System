import time


class DuplicateSuppressor:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._seen: dict[tuple[int, str], float] = {}

    def should_emit(self, camera_id: int, plate_text: str) -> bool:
        now = time.time()
        key = (camera_id, plate_text)
        self._purge(now)
        if now - self._seen.get(key, 0) < self.ttl_seconds:
            return False
        self._seen[key] = now
        return True

    def _purge(self, now: float) -> None:
        expired = [key for key, value in self._seen.items() if now - value > self.ttl_seconds]
        for key in expired:
            self._seen.pop(key, None)
