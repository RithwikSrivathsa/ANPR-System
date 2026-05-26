import { Activity, Camera, WifiOff } from "lucide-react";
import { previewUrl } from "../api/client";
import type { Camera as CameraType, Detection } from "../types";

export function CameraCard({ camera, latest }: { camera: CameraType; latest?: Detection }) {
  const online = camera.status === "online";
  return (
    <div className="glass overflow-hidden rounded-lg">
      <div className="relative aspect-video bg-black/70">
        {online && <img src={previewUrl(camera.id)} className="absolute inset-0 h-full w-full object-cover" />}
        <div className="absolute inset-0 grid place-items-center text-slate-500">
          {!online && <Camera size={42} />}
        </div>
        {latest?.bbox && <div className="absolute left-[22%] top-[44%] h-[18%] w-[45%] rounded border-2 border-mint shadow-glow" />}
        <div className="absolute left-3 top-3 rounded-md bg-black/60 px-2 py-1 text-xs">{camera.name}</div>
        <div className="absolute bottom-3 right-3 rounded-md bg-black/60 px-2 py-1 text-xs text-mint">{camera.fps.toFixed(1)} FPS</div>
      </div>
      <div className="flex items-center justify-between p-4">
        <div>
          <p className="text-sm text-slate-400">Status</p>
          <p className={online ? "text-mint" : "text-coral"}>{camera.status}</p>
        </div>
        {online ? <Activity className="text-mint" /> : <WifiOff className="text-coral" />}
      </div>
      {latest && (
        <div className="border-t border-line px-4 py-3 text-sm">
          <span className="text-slate-400">Latest plate </span>
          <span className="font-mono text-amber">{latest.plate_text}</span>
        </div>
      )}
    </div>
  );
}
