import type { LucideIcon } from "lucide-react";

export function StatCard({ label, value, icon: Icon, tone }: { label: string; value: string | number; icon: LucideIcon; tone: string }) {
  return (
    <div className="glass rounded-lg p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">{label}</span>
        <Icon className={tone} size={20} />
      </div>
      <div className="mt-3 text-3xl font-semibold tracking-normal">{value}</div>
    </div>
  );
}
