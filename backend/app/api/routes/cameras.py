from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Camera
from app.schemas import CameraCreate, CameraRead

router = APIRouter()


@router.get("", response_model=list[CameraRead])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).order_by(Camera.id.desc()).all()


@router.post("", response_model=CameraRead, status_code=201)
async def create_camera(payload: CameraCreate, request: Request, db: Session = Depends(get_db)):
    camera = Camera(**payload.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    if camera.enabled:
        await request.app.state.camera_manager.start_camera(camera.id)
    return camera


@router.delete("/{camera_id}", status_code=204)
async def delete_camera(camera_id: int, request: Request, db: Session = Depends(get_db)):
    camera = db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    await request.app.state.camera_manager.stop_camera(camera_id)
    db.delete(camera)
    db.commit()
