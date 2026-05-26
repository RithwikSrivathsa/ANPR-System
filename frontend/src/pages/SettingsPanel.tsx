import { Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { getSettings, updateSettings } from "../api/client";
import { useAnprStore } from "../store/useAnprStore";

export function SettingsPanel() {
  const { cameras, addCamera, removeCamera } = useAnprStore();
  const [name, setName] = useState("");
  const [rtsp, setRtsp] = useState("");
  const [duplicateTimeout, setDuplicateTimeout] = useState(300);
  const [ocrThreshold, setOcrThreshold] = useState(0.8);
  const [savingCamera, setSavingCamera] = useState(false);

  useEffect(() => {
    void getSettings().then((settings) => {
      setDuplicateTimeout(settings.duplicate_timeout_seconds);
      setOcrThreshold(settings.ocr_confidence_threshold);
    });
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSavingCamera(true);
    try {
      await addCamera({ name, rtsp_url: rtsp, enabled: true });
      setName("");
      setRtsp("");
    } finally {
      setSavingCamera(false);
    }
  };

  return (
    <section id="settings" className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
      <form onSubmit={submit} className="glass rounded-lg p-4">
        <h2 className="mb-4 text-lg font-semibold">Add RTSP Camera</h2>
        <label className="mb-3 block text-sm text-slate-400">
          Camera name
          <input value={name} onChange={(e) => setName(e.target.value)} className="mt-2 w-full rounded-md border border-line bg-white/5 px-3 py-2 text-white outline-none focus:border-mint" required />
        </label>
        <label className="mb-4 block text-sm text-slate-400">
          RTSP URL
          <input value={rtsp} onChange={(e) => setRtsp(e.target.value)} placeholder="rtsp://user:pass@host:554/stream1" className="mt-2 w-full rounded-md border border-line bg-white/5 px-3 py-2 text-white outline-none focus:border-mint" required />
        </label>
        <button disabled={savingCamera} className="flex items-center gap-2 rounded-md bg-mint px-4 py-2 font-semibold text-ink disabled:cursor-wait disabled:opacity-60">
          <Plus size={18} />
          {savingCamera ? "Adding..." : "Add camera"}
        </button>
      </form>
      <div className="glass rounded-lg p-4">
        <h2 className="mb-4 text-lg font-semibold">Camera Registry</h2>
        <div className="space-y-3">
          {cameras.map((camera) => (
            <div key={camera.id} className="flex items-center justify-between rounded-md border border-line p-3">
              <div>
                <p className="font-medium">{camera.name}</p>
                <p className="max-w-[48rem] truncate text-xs text-slate-500">{camera.rtsp_url}</p>
              </div>
              <button aria-label="Remove camera" onClick={() => removeCamera(camera.id)} className="rounded-md p-2 text-slate-400 hover:bg-coral/15 hover:text-coral">
                <Trash2 size={17} />
              </button>
            </div>
          ))}
        </div>
      </div>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          await updateSettings({ duplicate_timeout_seconds: duplicateTimeout, ocr_confidence_threshold: ocrThreshold });
        }}
        className="glass rounded-lg p-4 xl:col-span-2"
      >
        <h2 className="mb-4 text-lg font-semibold">Recognition Settings</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="text-sm text-slate-400">
            Duplicate timeout
            <input type="number" min={1} value={duplicateTimeout} onChange={(e) => setDuplicateTimeout(Number(e.target.value))} className="mt-2 w-full rounded-md border border-line bg-white/5 px-3 py-2 text-white outline-none focus:border-mint" />
          </label>
          <label className="text-sm text-slate-400">
            OCR confidence threshold
            <input type="number" min={0} max={1} step={0.01} value={ocrThreshold} onChange={(e) => setOcrThreshold(Number(e.target.value))} className="mt-2 w-full rounded-md border border-line bg-white/5 px-3 py-2 text-white outline-none focus:border-mint" />
          </label>
        </div>
        <button className="mt-4 rounded-md bg-amber px-4 py-2 font-semibold text-ink">Save settings</button>
      </form>
    </section>
  );
}
