from pathlib import Path
import shutil

from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.models import Camera, Detection, SystemLog

logger = get_logger(__name__)


def reset_runtime_data(session_factory: sessionmaker) -> None:
    if not settings.reset_data_on_start:
        return
    with session_factory() as db:
        db.query(SystemLog).delete()
        db.query(Detection).delete()
        db.query(Camera).delete()
        db.commit()

    snapshot_root = Path(settings.snapshot_dir)
    if snapshot_root.exists():
        for child in snapshot_root.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
    logger.warning("RESET_DATA_ON_START=true cleared cameras, detections, logs, and snapshots")
