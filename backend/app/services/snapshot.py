from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings


def save_snapshot(camera_id: int, plate_text: str, image: np.ndarray) -> str:
    now = datetime.now(timezone.utc)
    folder = Path(settings.snapshot_dir) / str(camera_id) / now.strftime("%Y%m%d")
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{now.strftime('%H%M%S_%f')}_{plate_text}.jpg"
    path = folder / filename
    cv2.imwrite(str(path), image)
    return str(path)
