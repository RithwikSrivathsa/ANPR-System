import { BarChart3, Camera, Gauge, ScrollText, Settings, Table2 } from "lucide-react";

const items = [
  { href: "#live", label: "Live", icon: Gauge },
  { href: "#detections", label: "Detections", icon: Table2 },
  { href: "#logs", label: "Logs", icon: ScrollText },
  { href: "#analytics", label: "Analytics", icon: BarChart3 },
  { href: "#settings", label: "Settings", icon: Settings }
];

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-ink/90 px-4 py-6 backdrop-blur-xl lg:block">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-md bg-mint/15 text-mint">
          <Camera size={24} />
        </div>
        <div>
          <h1 className="text-lg font-semibold">ANPR Command</h1>
          <p className="text-xs text-slate-400">Realtime plate intelligence</p>
        </div>
      </div>
      <nav className="space-y-2">
        {items.map((item) => (
          <a key={item.href} href={item.href} className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-300 transition hover:bg-white/8 hover:text-white">
            <item.icon size={18} />
            {item.label}
          </a>
        ))}
      </nav>
      <div className="absolute bottom-6 left-4 right-4 rounded-lg border border-line bg-white/5 p-3">
        <p className="text-xs font-medium text-slate-300">Backend API</p>
        <a href="http://localhost:8000/docs" target="_blank" className="mt-2 block truncate text-sm text-mint hover:text-white">
          localhost:8000/docs
        </a>
      </div>
    </aside>
  );
}
