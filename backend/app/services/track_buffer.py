from collections import Counter
from dataclasses import dataclass, field
import time

import cv2
import numpy as np

from app.core.config import settings


@dataclass(slots=True)
class TrackCandidate:
    track_id: int
    bbox: tuple[int, int, int, int]
    crop: np.ndarray
    detection_confidence: float
    frame_count: int
    captured_at: float
    sharpness: float

    @property
    def quality(self) -> float:
        x1, y1, x2, y2 = self.bbox
        area_score = min(1.0, ((x2 - x1) * (y2 - y1)) / 45000)
        sharpness_score = min(1.0, self.sharpness / 450)
        return (self.detection_confidence * 0.45) + (sharpness_score * 0.40) + (area_score * 0.15)


@dataclass
class TrackWindow:
    track_id: int
    started_at: float
    last_seen_at: float
    candidates: list[TrackCandidate] = field(default_factory=list)


class TrackCandidateBuffer:
    def __init__(self) -> None:
        self._tracks: dict[int, TrackWindow] = {}

    def add(
        self,
        track_id: int,
        bbox: tuple[int, int, int, int],
        crop: np.ndarray,
        detection_confidence: float,
        frame_count: int,
    ) -> None:
        now = time.time()
        window = self._tracks.setdefault(track_id, TrackWindow(track_id=track_id, started_at=now, last_seen_at=now))
        window.last_seen_at = now
        candidate = TrackCandidate(
            track_id=track_id,
            bbox=bbox,
            crop=crop.copy(),
            detection_confidence=detection_confidence,
            frame_count=frame_count,
            captured_at=now,
            sharpness=self._sharpness(crop),
        )
        window.candidates.append(candidate)
        window.candidates = sorted(window.candidates, key=lambda item: item.quality, reverse=True)[
            : settings.track_max_candidates
        ]

    def pop_ready(self) -> list[TrackWindow]:
        now = time.time()
        ready_ids = [
            track_id
            for track_id, window in self._tracks.items()
            if now - window.started_at >= settings.track_capture_window_seconds
        ]
        return [self._tracks.pop(track_id) for track_id in ready_ids]

    def pop_stale(self) -> list[TrackWindow]:
        now = time.time()
        stale_ids = [
            track_id
            for track_id, window in self._tracks.items()
            if now - window.last_seen_at >= settings.track_stale_seconds
        ]
        return [self._tracks.pop(track_id) for track_id in stale_ids]

    @staticmethod
    def best_text(reads: list[tuple[str, float]]) -> tuple[str | None, float]:
        if not reads:
            return None, 0.0
        vote_counts = Counter(text for text, _ in reads)
        scored = []
        for text, count in vote_counts.items():
            confidences = [confidence for candidate_text, confidence in reads if candidate_text == text]
            scored.append((text, count, sum(confidences) / len(confidences), max(confidences)))
        text, count, average_conf, max_conf = max(scored, key=lambda item: (item[1], item[2], len(item[0])))
        confidence = min(0.99, max(max_conf, average_conf + (0.03 * (count - 1))))
        return text, confidence

    @staticmethod
    def _sharpness(image: np.ndarray) -> float:
        if image.size == 0:
            return 0.0
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
