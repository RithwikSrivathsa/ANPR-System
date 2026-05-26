import { AlertTriangle, CheckCircle2, Radio } from "lucide-react";
import type { Camera, SystemLog } from "../types";
import { formatIst } from "../utils/time";

export function LogsPanel({ logs, cameras }: { logs: SystemLog[]; cameras: Camera[] }) {
  const cameraName = (id?: number | null) => cameras.find((camera) => camera.id === id)?.name ?? "System";

  return (
    <section id="logs" className="glass rounded-lg">
      <div className="border-b border-line p-4">
        <h2 className="text-lg font-semibold">Operations Log</h2>
        <p className="text-xs text-slate-400">Capture, OCR, duplicate removal, and stream events</p>
      </div>
      <div className="max-h-[42rem] overflow-y-auto">
        {logs.map((log) => (
          <div key={log.id} className="grid grid-cols-[1.5rem_1fr] gap-3 border-b border-line px-4 py-3 text-sm">
            <div className={log.level === "warning" ? "text-amber" : log.message.includes("saved") ? "text-mint" : "text-slate-400"}>
              {log.level === "warning" ? <AlertTriangle size={17} /> : log.message.includes("saved") ? <CheckCircle2 size={17} /> : <Radio size={17} />}
            </div>
            <div>
              <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
                <span className={log.level === "warning" ? "font-medium text-amber" : "font-medium text-mint"}>{cameraName(log.camera_id)}</span>
                <span className="text-xs text-slate-500">{formatIst(log.created_at)}</span>
              </div>
              <p className="break-words font-mono text-xs leading-5 text-slate-300">{log.message}</p>
            </div>
          </div>
        ))}
        {logs.length === 0 && <div className="p-6 text-center text-slate-400">No processing logs yet.</div>}
      </div>
    </section>
  );
}
