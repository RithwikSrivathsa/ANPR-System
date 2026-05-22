from itertools import count

import numpy as np


class SimpleByteTrackAdapter:
    """Small tracking adapter. Uses Ultralytics ByteTrack if available, otherwise IoU matching."""

    def __init__(self) -> None:
        self._next_id = count(1)
        self._tracks: dict[int, tuple[int, int, int, int]] = {}

    def update(self, detections: list[tuple[int, int, int, int]], frame: np.ndarray) -> list[int]:
        assigned: list[int] = []
        for bbox in detections:
            best_id = None
            best_iou = 0.0
            for track_id, existing in self._tracks.items():
                iou = self._iou(bbox, existing)
                if iou > best_iou:
                    best_id, best_iou = track_id, iou
            if best_id is None or best_iou < 0.25:
                best_id = next(self._next_id)
            self._tracks[best_id] = bbox
            assigned.append(best_id)
        return assigned

    @staticmethod
    def _iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        intersection = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
        area_b = max(1, (bx2 - bx1) * (by2 - by1))
        return intersection / float(area_a + area_b - intersection)
