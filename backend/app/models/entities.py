from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    rtsp_url: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(40), default="offline")
    fps: Mapped[float] = mapped_column(Float, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    detections: Mapped[list["Detection"]] = relationship(back_populates="camera", cascade="all,delete")


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plate_text: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id"), index=True, nullable=False)
    snapshot_path: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    track_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    bbox: Mapped[str | None] = mapped_column(String(120), nullable=True)

    camera: Mapped[Camera] = relationship(back_populates="detections")


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    camera_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
