import axios from "axios";
import type { Analytics, Camera, Detection, SystemLog } from "../types";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15000
});

export const listCameras = async () => (await api.get<Camera[]>("/cameras")).data;
export const createCamera = async (payload: Pick<Camera, "name" | "rtsp_url" | "enabled">) =>
  (await api.post<Camera>("/cameras", payload)).data;
export const deleteCamera = async (id: number) => api.delete(`/cameras/${id}`);
export const listDetections = async (params?: Record<string, string | number | undefined>) =>
  (await api.get<Detection[]>("/detections", { params })).data;
export const deleteDetection = async (id: number) => api.delete(`/detections/${id}`);
export const getAnalytics = async () => (await api.get<Analytics>("/analytics")).data;
export const listLogs = async (params?: Record<string, string | number | undefined>) =>
  (await api.get<SystemLog[]>("/logs", { params })).data;
export const getSettings = async () => (await api.get<{ duplicate_timeout_seconds: number; ocr_confidence_threshold: number }>("/settings")).data;
export const updateSettings = async (payload: { duplicate_timeout_seconds?: number; ocr_confidence_threshold?: number }) =>
  (await api.patch("/settings", payload)).data;

export const snapshotUrl = (path: string) => {
  const marker = "snapshots";
  const index = path.replaceAll("\\", "/").lastIndexOf(marker);
  return index >= 0 ? `${API_URL}/${path.replaceAll("\\", "/").slice(index)}` : path;
};

export const previewUrl = (cameraId: number) => `${API_URL}/cameras/${cameraId}/preview`;
