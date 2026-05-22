import re

import cv2
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class PlateOCR:
    def __init__(self) -> None:
        self.reader = None
        try:
            from paddleocr import PaddleOCR

            self.reader = PaddleOCR(use_angle_cls=True, lang="en", show_log=False, use_gpu=False)
        except Exception as exc:
            logger.warning("PaddleOCR unavailable until dependencies/model initialize: %s", exc)

    def read(self, plate_crop: np.ndarray) -> tuple[str | None, float]:
        if self.reader is None or plate_crop.size == 0:
            return None, 0.0
        processed = self.preprocess(plate_crop)
        try:
            result = self.reader.ocr(processed, cls=True)
        except Exception as exc:
            logger.exception("OCR failed: %s", exc)
            return None, 0.0

        candidates: list[tuple[str, float]] = []
        for block in result or []:
            for item in block or []:
                text, conf = item[1][0], float(item[1][1])
                cleaned = self.clean_text(text)
                if cleaned:
                    candidates.append((cleaned, conf))
        if not candidates:
            return None, 0.0
        text, confidence = max(candidates, key=lambda value: value[1])
        if confidence < settings.ocr_confidence_threshold:
            return None, confidence
        return text, confidence

    @staticmethod
    def preprocess(image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        gray = cv2.equalizeHist(gray)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 9
        )
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def clean_text(text: str) -> str:
        cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
        cleaned = cleaned.replace(" ", "")
        if len(cleaned) < 4 or len(cleaned) > 14:
            return ""
        return cleaned
