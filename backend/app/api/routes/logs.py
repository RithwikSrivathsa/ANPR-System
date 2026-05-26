from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import SystemLog
from app.schemas import SystemLogRead

router = APIRouter()


@router.get("", response_model=list[SystemLogRead])
def list_logs(
    camera_id: int | None = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(SystemLog)
    if camera_id:
        query = query.filter(SystemLog.camera_id == camera_id)
    return query.order_by(SystemLog.created_at.desc()).limit(limit).all()
