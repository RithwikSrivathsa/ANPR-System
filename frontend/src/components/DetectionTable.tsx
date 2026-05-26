import { Download, Image, Trash2 } from "lucide-react";
import { snapshotUrl } from "../api/client";
import type { Camera, Detection } from "../types";
import { formatIst } from "../utils/time";

export function DetectionTable({
  detections,
  cameras,
  onDelete
}: {
  detections: Detection[];
  cameras: Camera[];
  onDelete: (id: number) => void;
}) {
  const cameraName = (id: number) => cameras.find((camera) => camera.id === id)?.name ?? `Camera ${id}`;
  return (
    <div className="glass rounded-lg">
      <div className="flex items-center justify-between border-b border-line p-4">
        <div>
          <h2 className="text-lg font-semibold">Detection Register</h2>
          <p className="text-xs text-slate-400">Verified plate reads with crop snapshots and confidence</p>
        </div>
        <a href={`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/detections/export.csv`} className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm hover:bg-white/8">
          <Download size={16} />
          CSV
        </a>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[780px] text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th className="p-4">Plate</th>
              <th className="p-4">Time</th>
              <th className="p-4">Camera</th>
              <th className="p-4">Evidence</th>
              <th className="p-4">Confidence</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {detections.map((detection, index) => (
              <tr key={detection.id} className={`border-t border-line ${index === 0 ? "plate-pulse" : ""}`}>
                <td className="p-4">
                  <span className="rounded-md border border-amber/30 bg-amber/10 px-2.5 py-1 font-mono text-base text-amber">
                    {detection.plate_text}
                  </span>
                </td>
                <td className="p-4 text-slate-300">{formatIst(detection.detected_at)}</td>
                <td className="p-4">{detection.camera_name ?? cameraName(detection.camera_id)}</td>
                <td className="p-4">
                  {detection.snapshot_path ? (
                    <img src={snapshotUrl(detection.snapshot_path)} className="h-12 w-28 rounded-md border border-line object-cover" />
                  ) : (
                    <div className="grid h-12 w-28 place-items-center rounded-md border border-line text-slate-500">
                      <Image size={16} />
                    </div>
                  )}
                </td>
                <td className="p-4">
                  <div className="h-2 w-20 overflow-hidden rounded-full bg-white/10">
                    <div className="h-full rounded-full bg-mint" style={{ width: `${Math.round(detection.confidence * 100)}%` }} />
                  </div>
                  <span className="mt-1 block text-xs text-slate-400">{Math.round(detection.confidence * 100)}%</span>
                </td>
                <td className="p-4">
                  <button aria-label="Delete detection" onClick={() => onDelete(detection.id)} className="rounded-md p-2 text-slate-400 hover:bg-coral/15 hover:text-coral">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {detections.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-400">
                  No detections match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
