"use client";

import { useState } from "react";
import { AnalysisResponse } from "@/types/report";
import { Bot, Send, User, Loader2, Sparkles } from "lucide-react";

interface ReportChatProps {
  result: AnalysisResponse;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ReportChat({ result }: ReportChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! আমি আপনার রিপোর্টটি বিশ্লেষণ করেছি। রিপোর্টটি নিয়ে আপনার যেকোনো প্রশ্ন ইংরেজি বা বাংলায় জিজ্ঞেস করতে পারেন (যেমন: 'আমার কী সমস্যা হয়েছে?' বা 'কী খাবার খাওয়া উচিত?')।",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setSending(true);

    const reportContext = result.findings
      .map((f) => `${f.test}: ${f.value} ${f.unit} (${f.status}, Ref: ${f.min}-${f.max})`)
      .join("\n");

    try {
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          report_context: `Report Type: ${result.report_type || "Medical Report"}\nPrimary Finding: ${result.ml_insight.category}\nSummary: ${result.ml_insight.detailed_explanation || ""}\nBiomarkers:\n${reportContext}`,
          age: result.patient.age,
          gender: result.patient.gender,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to get response.");

      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "দুঃখিত, এই মুহূর্তে সার্ভারের সাথে সংযোগ করা যাচ্ছে না।" },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-600 text-white">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Ask MediSense AI Chatbot</h3>
            <p className="text-xs text-slate-500">Ask follow-up questions in English or বাংলা</p>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-teal-50 px-2.5 py-1 text-xs font-medium text-teal-700">
          <Sparkles className="h-3 w-3" /> Context-Aware AI
        </span>
      </div>

      <div className="max-h-80 space-y-4 overflow-y-auto p-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${
              msg.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                msg.role === "user" ? "bg-slate-800 text-white" : "bg-teal-100 text-teal-700"
              }`}
            >
              {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line ${
                msg.role === "user"
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-800"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin text-teal-600" />
            <span>MediSense AI is analyzing your question...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="flex gap-2 border-t border-slate-100 p-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about your report (e.g., আমার রিপোর্টে কী রোগের লক্ষণ দেখা যাচ্ছে?)..."
          className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-600/20"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="flex items-center gap-1.5 rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
}