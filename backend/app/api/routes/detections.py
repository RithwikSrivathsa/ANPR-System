from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Camera, Detection
from app.schemas import DetectionRead

router = APIRouter()


@router.get("", response_model=list[DetectionRead])
def list_detections(
    plate: str | None = None,
    camera_id: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(Detection)
    if plate:
        query = query.filter(Detection.plate_text.ilike(f"%{plate}%"))
    if camera_id:
        query = query.filter(Detection.camera_id == camera_id)
    if start:
        query = query.filter(Detection.detected_at >= start)
    if end:
        query = query.filter(Detection.detected_at <= end)
    return query.order_by(Detection.detected_at.desc()).limit(limit).all()


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    rows = (
        db.query(Detection, Camera.name)
        .join(Camera, Detection.camera_id == Camera.id)
        .order_by(Detection.detected_at.desc())
        .all()
    )

    def stream():
        yield "id,plate_text,confidence,camera,detected_at,track_id,snapshot_path\n"
        for detection, camera_name in rows:
            yield (
                f"{detection.id},{detection.plate_text},{detection.confidence},{camera_name},"
                f"{detection.detected_at},{detection.track_id or ''},{detection.snapshot_path}\n"
            )

    return StreamingResponse(stream(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=detections.csv"})


@router.get("/{detection_id}", response_model=DetectionRead)
def get_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = db.get(Detection, detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.delete("/{detection_id}", status_code=204)
def delete_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = db.get(Detection, detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    db.delete(detection)
    db.commit()
