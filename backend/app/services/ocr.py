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

            self.reader = PaddleOCR(use_angle_cls=True, lang="en", show_log=False, use_gpu=settings.paddle_use_gpu)
        except Exception as exc:
            logger.warning("PaddleOCR unavailable until dependencies/model initialize: %s", exc)

    def read(self, plate_crop: np.ndarray) -> tuple[str | None, float]:
        if self.reader is None or plate_crop.size == 0:
            return None, 0.0
        images = self.preprocess_variants(plate_crop)
        best_text: str | None = None
        best_confidence = 0.0
        try:
            for image in images:
                result = self.reader.ocr(image, cls=True)
                text, confidence = self._parse_result(result)
                if text and confidence > best_confidence:
                    best_text, best_confidence = text, confidence
        except Exception as exc:
            logger.exception("OCR failed: %s", exc)
            return None, 0.0

        if not best_text:
            return None, best_confidence
        if best_confidence < settings.ocr_confidence_threshold:
            return None, best_confidence
        return best_text, best_confidence

    def _parse_result(self, result) -> tuple[str | None, float]:
        lines: list[tuple[float, float, str, float]] = []
        for block in result or []:
            for item in block or []:
                points = item[0]
                x = min(point[0] for point in points)
                y = min(point[1] for point in points)
                text, conf = item[1][0], float(item[1][1])
                lines.append((y, x, text, conf))
        if not lines:
            return None, 0.0

        ordered = sorted(lines, key=lambda value: (round(value[0] / 18), value[1]))
        joined = "".join(line[2] for line in ordered)
        cleaned = self.clean_text(joined)
        confidence = sum(line[3] for line in ordered) / len(ordered)
        if not cleaned:
            single_line_candidates = [(self.clean_text(line[2]), line[3]) for line in ordered]
            single_line_candidates = [candidate for candidate in single_line_candidates if candidate[0]]
            if not single_line_candidates:
                return None, confidence
            return max(single_line_candidates, key=lambda value: value[1])
        return cleaned, confidence

    @staticmethod
    def preprocess_variants(image: np.ndarray) -> list[np.ndarray]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 9
        )
        inverted = cv2.bitwise_not(thresh)
        return [image, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR), cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)]

    @staticmethod
    def clean_text(text: str) -> str:
        cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
        cleaned = cleaned.replace("IND", "")
        cleaned = re.sub(r"^(IN|ND)", "", cleaned)
        matches = re.findall(r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}", cleaned)
        if matches:
            return max(matches, key=len)
        if len(cleaned) < 7 or len(cleaned) > 14:
            return ""
        if len(re.findall(r"[A-Z]", cleaned)) < 2 or len(re.findall(r"[0-9]", cleaned)) < 4:
            return ""
        return cleaned
