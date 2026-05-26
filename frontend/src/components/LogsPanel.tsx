import type { Camera, SystemLog } from "../types";
import { formatIst } from "../utils/time";

export function LogsPanel({ logs, cameras }: { logs: SystemLog[]; cameras: Camera[] }) {
  const cameraName = (id?: number | null) => cameras.find((camera) => camera.id === id)?.name ?? "System";

  return (
    <section className="glass mb-6 rounded-lg">
      <div className="border-b border-line p-4">
        <h2 className="text-lg font-semibold">Processing Logs</h2>
      </div>
      <div className="max-h-80 overflow-y-auto">
        {logs.map((log) => (
          <div key={log.id} className="grid gap-2 border-b border-line px-4 py-3 text-sm md:grid-cols-[12rem_8rem_1fr]">
            <span className="text-slate-400">{formatIst(log.created_at)}</span>
            <span className={log.level === "warning" ? "text-amber" : "text-mint"}>{cameraName(log.camera_id)}</span>
            <span className="font-mono text-slate-300">{log.message}</span>
          </div>
        ))}
        {logs.length === 0 && <div className="p-6 text-center text-slate-400">No processing logs yet.</div>}
      </div>
    </section>
  );
}
