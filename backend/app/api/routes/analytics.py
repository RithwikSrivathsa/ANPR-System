from datetime import datetime, timedelta, timezone

import psutil
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Camera, Detection

router = APIRouter()


@router.get("")
def analytics(db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    total = db.query(func.count(Detection.id)).scalar() or 0
    today = db.query(func.count(Detection.id)).filter(Detection.detected_at >= since).scalar() or 0
    hourly = (
        db.query(func.strftime("%H:00", Detection.detected_at), func.count(Detection.id))
        .filter(Detection.detected_at >= since)
        .group_by(func.strftime("%H", Detection.detected_at))
        .all()
    )
    frequent = (
        db.query(Detection.plate_text, func.count(Detection.id).label("count"))
        .group_by(Detection.plate_text)
        .order_by(func.count(Detection.id).desc())
        .limit(10)
        .all()
    )
    cameras = db.query(func.count(Camera.id)).scalar() or 0
    online = db.query(func.count(Camera.id)).filter(Camera.status == "online").scalar() or 0
    return {
        "total_detections": total,
        "detections_24h": today,
        "camera_count": cameras,
        "online_cameras": online,
        "hourly": [{"hour": hour, "count": count} for hour, count in hourly],
        "frequent": [{"plate_text": plate, "count": count} for plate, count in frequent],
        "metrics": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
        },
    }
