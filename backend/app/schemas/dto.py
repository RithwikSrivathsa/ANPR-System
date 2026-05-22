from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CameraBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    rtsp_url: str = Field(min_length=4)
    enabled: bool = True


class CameraCreate(CameraBase):
    pass


class CameraRead(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    fps: float
    last_error: str | None = None
    created_at: datetime


class DetectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plate_text: str
    confidence: float
    camera_id: int
    snapshot_path: str
    detected_at: datetime
    track_id: int | None = None
    bbox: str | None = None


class DetectionEvent(DetectionRead):
    camera_name: str
    type: str = "detection"


class SettingsUpdate(BaseModel):
    duplicate_timeout_seconds: int | None = Field(default=None, ge=1)
    ocr_confidence_threshold: float | None = Field(default=None, ge=0, le=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
