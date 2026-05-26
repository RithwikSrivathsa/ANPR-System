from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ANPR System"
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./data/anpr.db"
    redis_url: str = "redis://localhost:6379/0"
    snapshot_dir: str = "./snapshots"
    model_path: str = "./models/license_plate_yolov8.pt"
    yolo_device: str = "auto"
    frame_skip: int = Field(default=3, ge=1)
    max_queue_size: int = Field(default=8, ge=1)
    duplicate_timeout_seconds: int = Field(default=300, ge=1)
    ocr_confidence_threshold: float = Field(default=0.65, ge=0, le=1)
    detection_confidence_threshold: float = Field(default=0.35, ge=0, le=1)
    paddle_use_gpu: bool = False
    plate_min_aspect_ratio: float = Field(default=1.8, gt=0)
    plate_max_aspect_ratio: float = Field(default=7.5, gt=0)
    plate_crop_padding_x: float = Field(default=0.35, ge=0, le=2)
    plate_crop_padding_y: float = Field(default=0.35, ge=0, le=2)
    frame_ignore_top_ratio: float = Field(default=0.12, ge=0, le=0.5)
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def ensure_dirs(self) -> None:
        Path(self.snapshot_dir).mkdir(parents=True, exist_ok=True)
        db_path = self.database_url.replace("sqlite:///", "")
        if not db_path.startswith(":memory:"):
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    cfg = Settings()
    cfg.ensure_dirs()
    return cfg


settings = get_settings()
