import { Download, Trash2 } from "lucide-react";
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
        <h2 className="text-lg font-semibold">Detection Log</h2>
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
              <th className="p-4">Snapshot</th>
              <th className="p-4">Confidence</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {detections.map((detection, index) => (
              <tr key={detection.id} className={`border-t border-line ${index === 0 ? "plate-pulse" : ""}`}>
                <td className="p-4 font-mono text-base text-amber">{detection.plate_text}</td>
                <td className="p-4 text-slate-300">{formatIst(detection.detected_at)}</td>
                <td className="p-4">{detection.camera_name ?? cameraName(detection.camera_id)}</td>
                <td className="p-4">
                  <img src={snapshotUrl(detection.snapshot_path)} className="h-12 w-24 rounded object-cover" />
                </td>
                <td className="p-4">{Math.round(detection.confidence * 100)}%</td>
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
