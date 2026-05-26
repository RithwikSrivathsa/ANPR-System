import { Activity, Camera, Clock, WifiOff } from "lucide-react";
import { previewUrl } from "../api/client";
import type { Camera as CameraType, Detection } from "../types";
import { formatIst } from "../utils/time";

export function CameraCard({ camera, latest }: { camera: CameraType; latest?: Detection }) {
  const online = camera.status === "online";
  return (
    <div className="glass overflow-hidden rounded-lg">
      <div className="relative aspect-video bg-black/80">
        {online && <img src={previewUrl(camera.id)} className="absolute inset-0 h-full w-full object-cover" />}
        <div className="absolute inset-0 bg-gradient-to-b from-black/35 via-transparent to-black/55" />
        <div className="absolute inset-0 grid place-items-center text-slate-500">
          {!online && (
            <div className="grid place-items-center gap-3 text-center">
              <Camera size={42} />
              <span className="text-sm">Waiting for camera stream</span>
            </div>
          )}
        </div>
        <div className="absolute left-3 top-3 flex items-center gap-2 rounded-md bg-black/65 px-2.5 py-1.5 text-xs">
          <span className={`h-2 w-2 rounded-full ${online ? "bg-mint" : "bg-coral"}`} />
          {camera.name}
        </div>
        <div className="absolute right-3 top-3 rounded-md bg-black/65 px-2.5 py-1.5 text-xs text-mint">{camera.fps.toFixed(1)} FPS</div>
        {latest && (
          <div className="absolute bottom-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2 rounded-md bg-black/70 px-3 py-2 text-xs">
            <span className="font-mono text-lg text-amber">{latest.plate_text}</span>
            <span className="flex items-center gap-1 text-slate-300">
              <Clock size={13} />
              {formatIst(latest.detected_at)}
            </span>
          </div>
        )}
      </div>
      <div className="flex items-center justify-between px-4 py-3">
        <div>
          <p className="text-xs text-slate-400">Stream status</p>
          <p className={online ? "font-medium text-mint" : "font-medium text-coral"}>{camera.status}</p>
        </div>
        {online ? <Activity className="text-mint" /> : <WifiOff className="text-coral" />}
      </div>
      {camera.last_error && <div className="border-t border-line px-4 py-2 text-xs text-amber">{camera.last_error}</div>}
    </div>
  );
}
