import { Activity, ShieldCheck } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-600 text-white shadow-sm">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              MediSense <span className="text-teal-600">AI</span>
            </span>
            <p className="text-xs text-slate-500">Clinical Report Interpreter</p>
          </div>
        </div>
        <div className="hidden items-center gap-2 rounded-full bg-teal-50 px-3.5 py-1.5 text-xs font-medium text-teal-800 sm:flex">
          <ShieldCheck className="h-4 w-4 text-teal-600" />
          <span>Privacy-First Analysis</span>
        </div>
      </div>
    </header>
  );
}