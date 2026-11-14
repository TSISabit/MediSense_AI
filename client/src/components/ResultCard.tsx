import { TestFinding } from "@/types/report";
import { AlertTriangle, CheckCircle2, Info } from "lucide-react";

interface ResultCardProps {
  item: TestFinding;
}

export default function ResultCard({ item }: ResultCardProps) {
  const isNormal = item.status === "NORMAL";
  const isLow = item.status === "LOW";

  const rangeSpan = item.max - item.min;
  const extendedMin = Math.max(0, item.min - rangeSpan * 0.4);
  const extendedMax = item.max + rangeSpan * 0.4;
  const percentage = Math.min(
    100,
    Math.max(5, ((item.value - extendedMin) / (extendedMax - extendedMin)) * 100)
  );

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{item.test}</h3>
          <p className="mt-0.5 text-xs text-slate-500">{item.description}</p>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
            isNormal
              ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
              : "bg-amber-50 text-amber-700 ring-1 ring-amber-600/20"
          }`}
        >
          {isNormal ? (
            <CheckCircle2 className="h-3.5 w-3.5" />
          ) : (
            <AlertTriangle className="h-3.5 w-3.5" />
          )}
          {item.status}
        </span>
      </div>

      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-slate-900">
          {item.value.toLocaleString()}
        </span>
        <span className="text-sm font-medium text-slate-500">{item.unit}</span>
        <span className="ml-auto text-xs text-slate-500">
          Normal: {item.min.toLocaleString()} – {item.max.toLocaleString()} {item.unit}
        </span>
      </div>

      <div className="mt-3">
        <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="absolute top-0 h-full bg-emerald-200"
            style={{ left: "22%", width: "56%" }}
          />
          <div
            className={`absolute top-0 h-full w-3 -translate-x-1/2 rounded-full ${
              isNormal ? "bg-emerald-600" : "bg-amber-500"
            }`}
            style={{ left: `${percentage}%` }}
          />
        </div>
      </div>

      <div className="mt-4 flex items-start gap-2 rounded-xl bg-slate-50 p-3 text-xs text-slate-700">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-teal-600" />
        <span>
          {item.interpretation}{" "}
          {!isNormal && (
            <strong className="font-medium text-slate-900">
              {isLow
                ? "Consider discussing iron/vitamin levels with a physician."
                : "Consult a healthcare provider for clinical evaluation."}
            </strong>
          )}
        </span>
      </div>
    </div>
  );
}