# ANPR System

Production-oriented Automatic Number Plate Recognition stack for RTSP cameras, YOLOv8 plate detection, PaddleOCR, SQLite logging, Redis realtime fanout, and a modern React dashboard.

## Architecture

- `backend`: FastAPI, OpenCV RTSP workers, YOLOv8 detector, PaddleOCR, SQLite, SQLAlchemy, Redis pub/sub, WebSockets.
- `frontend`: React, Vite, TailwindCSS, Zustand, Axios, Recharts, native WebSocket client.
- `models`: local YOLOv8 plate model storage.
- `data`: persistent SQLite database.
- `snapshots`: local plate crop snapshots.

## Quick Start

1. Optionally copy env files for local overrides:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

2. Add your YOLOv8 plate model:

```text
models/license_plate_yolov8.pt
```

3. Run:

```bash
docker compose up --build
```

4. Open:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8000/docs
```

## What To Do Next

1. Download a pretrained license plate YOLO model and place it at:

```text
models/license_plate_yolov8.pt
```

For quick testing, a public YOLOv8 license plate model can be downloaded from Hugging Face and renamed to `license_plate_yolov8.pt`.

2. Start the stack:

```bash
docker compose up --build
```

3. Add your RTSP camera from the dashboard Settings page. For example:

```text
rtsp://username:password@camera-ip:554/stream1
```

4. Test with real Indian lorry or water tanker footage. The pretrained detector should work for visible official plates, but painted tanker body numbers or unusual plate positions may require later fine-tuning.

5. Tune runtime settings from the dashboard:

- Duplicate timeout
- OCR confidence threshold
- Detection confidence threshold through backend environment variables
- Frame skipping through backend environment variables

6. Before production use:

- Replace `JWT_SECRET`.
- Restrict `CORS_ORIGINS`.
- Store RTSP credentials securely.
- Add HTTPS through a reverse proxy.
- Back up `data/anpr.db` and `snapshots`.
- Validate accuracy on day, night, rain, motion blur, and angled-camera samples.

## GPU Mode

Install NVIDIA Container Toolkit, then run:

```bash
docker compose --profile gpu up --build backend-gpu redis frontend
```

Set `YOLO_DEVICE=0` in `backend/.env` or compose environment. PaddleOCR is configured CPU-first for broad compatibility; switch it to GPU in `app/services/ocr.py` if your PaddlePaddle GPU build is installed.

## RTSP Cameras

Add cameras from the dashboard Settings panel or call:

```bash
curl -X POST http://localhost:8000/cameras \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Gate 1\",\"rtsp_url\":\"rtsp://user:pass@host:554/stream1\",\"enabled\":true}"
```

Sample camera payloads live in `docker/sample-cameras.json`.

## API

- `GET /health`
- `GET /detections`
- `GET /detections/{id}`
- `DELETE /detections/{id}`
- `GET /detections/export.csv`
- `GET /cameras`
- `POST /cameras`
- `DELETE /cameras/{id}`
- `GET /analytics`
- `GET /settings`
- `PATCH /settings`
- `WS /ws/detections`
- `POST /auth/login`

## Runtime Notes

- SQLite is stored in `data/anpr.db`.
- Snapshots are stored under `snapshots/{camera_id}/{date}`.
- Duplicate suppression is controlled by `DUPLICATE_TIMEOUT_SECONDS`.
- Frame skipping is controlled by `FRAME_SKIP`.
- RTSP reconnect uses exponential backoff up to 30 seconds.
- The backend starts even if CUDA, Redis, PaddleOCR, or the YOLO model are not immediately available; degraded services log warnings.

## Security Scaffold

JWT creation and password hashing utilities are included. The demo login endpoint accepts any non-empty credentials so local development is frictionless. Replace it with a users table or an external identity provider before exposing the system outside a trusted network.

## Training Model Expectations

Use a YOLOv8 model trained for license plate bounding boxes. The detector expects normal Ultralytics output and crops each detected plate for OCR preprocessing.

## Production Checklist

- Replace `JWT_SECRET`.
- Restrict `CORS_ORIGINS`.
- Put RTSP credentials in environment-managed secrets.
- Use HTTPS and a reverse proxy.
- Add backups for `data/anpr.db` and `snapshots`.
- Pin a CUDA-compatible PaddlePaddle GPU package if enabling OCR GPU.
