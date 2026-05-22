from fastapi import APIRouter

from app.core.config import settings
from app.schemas.dto import SettingsUpdate

router = APIRouter()


@router.get("")
def get_runtime_settings():
    return {
        "duplicate_timeout_seconds": settings.duplicate_timeout_seconds,
        "ocr_confidence_threshold": settings.ocr_confidence_threshold,
        "frame_skip": settings.frame_skip,
        "detection_confidence_threshold": settings.detection_confidence_threshold,
    }


@router.patch("")
def update_runtime_settings(payload: SettingsUpdate):
    if payload.duplicate_timeout_seconds is not None:
        settings.duplicate_timeout_seconds = payload.duplicate_timeout_seconds
    if payload.ocr_confidence_threshold is not None:
        settings.ocr_confidence_threshold = payload.ocr_confidence_threshold
    return get_runtime_settings()
