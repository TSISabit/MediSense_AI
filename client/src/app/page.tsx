"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import ResultCard from "@/components/ResultCard";
import { AnalysisResponse } from "@/types/report";
import {
  BrainCircuit,
  FileText,
  Loader2,
  Sparkles,
  UploadCloud,
  AlertCircle,
} from "lucide-react";

const SAMPLE_REPORT_TEXT = `COMPLETE BLOOD COUNT (CBC)
Hemoglobin: 10.2 g/dL
WBC: 12,500 /µL
Platelet: 250,000 /µL
RBC: 3.8 million/µL`;

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [age, setAge] = useState<number>(28);
  const [gender, setGender] = useState<"Male" | "Female">("Male");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleFileAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a PDF or Image report first, or click 'Try Sample CBC Data'.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("age", age.toString());
      formData.append("gender", gender);

      const res = await fetch(`${apiUrl}/api/analyze-file`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to analyze the uploaded report.");
      }
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Server connection failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleSampleDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/api/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: SAMPLE_REPORT_TEXT, age, gender }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Sample analysis failed.");
      }
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not connect to AI backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-teal-100/80 px-3.5 py-1 text-xs font-semibold text-teal-800">
            <Sparkles className="h-3.5 w-3.5" />
            <span>AI-Powered CBC Report Interpretation</span>
          </div>
          <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
            Understand Your Lab Results in Seconds
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-slate-600 sm:text-base">
            Upload a PDF or scanned image of your Complete Blood Count (CBC) report.
            MediSense AI extracts biomarkers, compares gender-specific clinical ranges,
            and highlights potential anomalies.
          </p>
        </div>

        <div className="mx-auto mt-8 max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <form onSubmit={handleFileAnalyze} className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600">
                  Patient Age
                </label>
                <input
                  type="number"
                  min={1}
                  max={120}
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  className="mt-1.5 w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-600/20"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600">
                  Biological Sex (For Reference Range)
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value as "Male" | "Female")}
                  className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-600/20"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>
            </div>

            <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50/70 px-6 py-8 text-center transition hover:border-teal-500 hover:bg-teal-50/30">
              <UploadCloud className="h-10 w-10 text-teal-600" />
              <span className="mt-3 text-sm font-semibold text-slate-800">
                {file ? file.name : "Click to upload medical report (PDF, JPG, PNG)"}
              </span>
              <span className="mt-1 text-xs text-slate-500">
                Supports digital lab PDFs and clear smartphone photos
              </span>
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
              />
            </label>

            {error && (
              <div className="flex items-center gap-2 rounded-xl bg-red-50 p-3.5 text-sm text-red-700">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                type="submit"
                disabled={loading}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-teal-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-teal-700 disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileText className="h-4 w-4" />
                )}
                <span>{loading ? "Analyzing Report..." : "Analyze Uploaded Report"}</span>
              </button>

              <button
                type="button"
                onClick={handleSampleDemo}
                disabled={loading}
                className="flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
              >
                <BrainCircuit className="h-4 w-4 text-teal-600" />
                <span>Try Sample CBC Data</span>
              </button>
            </div>
          </form>
        </div>

        {result && (
          <section className="mx-auto mt-10 max-w-4xl space-y-6">
            <div className="flex flex-col justify-between gap-4 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 p-6 text-white shadow-md sm:flex-row sm:items-center">
              <div>
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-teal-400">
                  <BrainCircuit className="h-4 w-4" />
                  <span>Random Forest Pattern Classification</span>
                </div>
                <h2 className="mt-1 text-2xl font-bold">
                  Primary Finding: {result.ml_insight.category}
                </h2>
                <p className="mt-1 text-xs text-slate-300">
                  Patient Profile: {result.patient.age} yrs, {result.patient.gender} • Model Confidence:{" "}
                  <span className="font-semibold text-teal-300">
                    {result.ml_insight.confidence}%
                  </span>
                </p>
              </div>
              <div className="rounded-xl bg-white/10 px-4 py-3 text-xs text-slate-200 backdrop-blur-sm">
                <strong>Medical Disclaimer:</strong> Educational & informational screening only. Not a clinical diagnosis.
              </div>
            </div>

            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              {result.findings.map((item) => (
                <ResultCard key={item.test} item={item} />
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}