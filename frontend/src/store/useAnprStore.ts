import { create } from "zustand";
import { createCamera, deleteCamera, getAnalytics, listCameras, listDetections, listLogs } from "../api/client";
import type { Analytics, Camera, Detection, SystemLog } from "../types";

type State = {
  cameras: Camera[];
  detections: Detection[];
  logs: SystemLog[];
  analytics?: Analytics;
  connected: boolean;
  loading: boolean;
  load: () => Promise<void>;
  addCamera: (payload: Pick<Camera, "name" | "rtsp_url" | "enabled">) => Promise<void>;
  removeCamera: (id: number) => Promise<void>;
  pushEvent: (event: Detection | { type: string; camera_id: number; status?: string; fps?: number }) => void;
};

export const useAnprStore = create<State>((set, get) => ({
  cameras: [],
  detections: [],
  logs: [],
  connected: false,
  loading: false,
  load: async () => {
    set({ loading: true });
    const [cameras, detections, analytics, logs] = await Promise.all([
      listCameras(),
      listDetections({ limit: 100 }),
      getAnalytics(),
      listLogs({ limit: 80 })
    ]);
    set({ cameras, detections, analytics, logs, loading: false });
  },
  addCamera: async (payload) => {
    const camera = await createCamera(payload);
    set({ cameras: [camera, ...get().cameras] });
  },
  removeCamera: async (id) => {
    await deleteCamera(id);
    set({ cameras: get().cameras.filter((camera) => camera.id !== id) });
  },
  pushEvent: (event) => {
    if (event.type === "detection" && "plate_text" in event) {
      set({ detections: [event, ...get().detections].slice(0, 150) });
      void getAnalytics().then((analytics) => set({ analytics }));
      return;
    }
    if (event.type === "camera_status") {
      set({
        cameras: get().cameras.map((camera) =>
          camera.id === event.camera_id
            ? { ...camera, status: event.status ?? camera.status, fps: event.fps ?? camera.fps }
            : camera
        )
      });
    }
  }
}));
