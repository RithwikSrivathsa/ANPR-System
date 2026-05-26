export type Camera = {
  id: number;
  name: string;
  rtsp_url: string;
  enabled: boolean;
  status: string;
  fps: number;
  last_error?: string | null;
  created_at: string;
};

export type Detection = {
  id: number;
  plate_text: string;
  confidence: number;
  camera_id: number;
  camera_name?: string;
  snapshot_path: string;
  detected_at: string;
  track_id?: number | null;
  bbox?: string | null;
  type?: string;
};

export type Analytics = {
  total_detections: number;
  detections_24h: number;
  camera_count: number;
  online_cameras: number;
  hourly: Array<{ hour: string; count: number }>;
  frequent: Array<{ plate_text: string; count: number }>;
  metrics: { cpu_percent: number; memory_percent: number };
};

export type SystemLog = {
  id: number;
  level: string;
  message: string;
  camera_id?: number | null;
  created_at: string;
};
