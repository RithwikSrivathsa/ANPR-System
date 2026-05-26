import { Activity, Camera, Cpu, Database } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { deleteDetection } from "./api/client";
import { CameraCard } from "./components/CameraCard";
import { DetectionTable } from "./components/DetectionTable";
import { LogsPanel } from "./components/LogsPanel";
import { Sidebar } from "./components/Sidebar";
import { StatCard } from "./components/StatCard";
import { SettingsPanel } from "./pages/SettingsPanel";
import { useAnprStore } from "./store/useAnprStore";
import { connectRealtime } from "./utils/realtime";

export function App() {
  const { cameras, detections, logs, analytics, connected, loading, load } = useAnprStore();
  const [plate, setPlate] = useState("");
  const [cameraFilter, setCameraFilter] = useState("");

  useEffect(() => {
    void load();
    const interval = window.setInterval(() => void load(), 15000);
    const disconnect = connectRealtime();
    return () => {
      window.clearInterval(interval);
      disconnect();
    };
  }, [load]);

  const filtered = useMemo(
    () =>
      detections.filter((detection) => {
        const plateMatch = detection.plate_text.toLowerCase().includes(plate.toLowerCase());
        const cameraMatch = cameraFilter ? detection.camera_id === Number(cameraFilter) : true;
        return plateMatch && cameraMatch;
      }),
    [detections, plate, cameraFilter]
  );

  const latestByCamera = (id: number) => detections.find((detection) => detection.camera_id === id);

  return (
    <div>
      <Sidebar />
      <main className="min-h-screen px-4 py-5 lg:ml-64 lg:px-8">
        <header className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <p className="text-sm uppercase text-mint">Realtime ANPR</p>
            <h1 className="text-3xl font-semibold tracking-normal">Automatic Number Plate Recognition</h1>
          </div>
          <div className={`rounded-md border px-3 py-2 text-sm ${connected ? "border-mint/40 text-mint" : "border-coral/40 text-coral"}`}>
            {connected ? "WebSocket connected" : "WebSocket offline"}
          </div>
        </header>

        <section className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Total detections" value={analytics?.total_detections ?? 0} icon={Database} tone="text-amber" />
          <StatCard label="Last 24 hours" value={analytics?.detections_24h ?? 0} icon={Activity} tone="text-mint" />
          <StatCard label="Online cameras" value={`${analytics?.online_cameras ?? 0}/${analytics?.camera_count ?? cameras.length}`} icon={Camera} tone="text-sky-300" />
          <StatCard label="CPU usage" value={`${Math.round(analytics?.metrics.cpu_percent ?? 0)}%`} icon={Cpu} tone="text-coral" />
        </section>

        <section id="live" className="mb-6">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Live Monitoring</h2>
            {loading && <span className="text-sm text-slate-400">Loading streams...</span>}
          </div>
          <div className="grid gap-4 xl:grid-cols-3">
            {cameras.map((camera) => (
              <CameraCard key={camera.id} camera={camera} latest={latestByCamera(camera.id)} />
            ))}
            {cameras.length === 0 && <div className="glass rounded-lg p-8 text-center text-slate-400 xl:col-span-3">Add an RTSP camera to start monitoring.</div>}
          </div>
        </section>

        <section id="detections" className="mb-6">
          <div className="mb-3 grid gap-3 md:grid-cols-[1fr_16rem]">
            <input value={plate} onChange={(e) => setPlate(e.target.value)} placeholder="Search plate" className="rounded-md border border-line bg-white/5 px-3 py-2 outline-none focus:border-mint" />
            <select value={cameraFilter} onChange={(e) => setCameraFilter(e.target.value)} className="rounded-md border border-line bg-white/5 px-3 py-2 outline-none focus:border-mint">
              <option value="">All cameras</option>
              {cameras.map((camera) => (
                <option key={camera.id} value={camera.id}>
                  {camera.name}
                </option>
              ))}
            </select>
          </div>
          <DetectionTable
            detections={filtered}
            cameras={cameras}
            onDelete={async (id) => {
              await deleteDetection(id);
              await load();
            }}
          />
        </section>

        <section id="analytics" className="mb-6 grid gap-4 xl:grid-cols-2">
          <div className="glass rounded-lg p-4">
            <h2 className="mb-4 text-lg font-semibold">Hourly Detections</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics?.hourly ?? []}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="hour" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ background: "#101820", border: "1px solid rgba(255,255,255,0.11)" }} />
                  <Area type="monotone" dataKey="count" stroke="#35f0b1" fill="rgba(53,240,177,0.18)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="glass rounded-lg p-4">
            <h2 className="mb-4 text-lg font-semibold">Frequent Vehicles</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics?.frequent ?? []}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="plate_text" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ background: "#101820", border: "1px solid rgba(255,255,255,0.11)" }} />
                  <Bar dataKey="count" fill="#f9c74f" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <LogsPanel logs={logs} cameras={cameras} />

        <SettingsPanel />
      </main>
    </div>
  );
}
