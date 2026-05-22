from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class PlateCandidate:
    bbox: tuple[int, int, int, int]
    confidence: float
    crop: np.ndarray


class PlateDetector:
    def __init__(self) -> None:
        self.model = None
        self.device = settings.yolo_device
        self._load()

    def _load(self) -> None:
        try:
            from ultralytics import YOLO

            model_path = Path(settings.model_path)
            if model_path.exists():
                self.model = YOLO(str(model_path))
            else:
                logger.warning("Plate model not found at %s. Detection will be disabled.", model_path)
        except Exception as exc:
            logger.warning("YOLO unavailable: %s", exc)

    def detect(self, frame: np.ndarray) -> list[PlateCandidate]:
        if self.model is None:
            return []
        device = None if self.device == "auto" else self.device
        results = self.model.predict(
            frame,
            conf=settings.detection_confidence_threshold,
            verbose=False,
            device=device,
        )
        candidates: list[PlateCandidate] = []
        height, width = frame.shape[:2]
        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            for box in boxes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width - 1, x2), min(height - 1, y2)
                if x2 <= x1 or y2 <= y1:
                    continue
                crop = frame[y1:y2, x1:x2]
                crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                candidates.append(PlateCandidate((x1, y1, x2, y2), conf, crop))
        return candidates
