"use client";
import { getApiUrl } from "@/lib/api";

import { useEffect, useState } from "react";
import { 
  FileText, 
  Clock, 
  TrendingUp, 
  CheckSquare, 
  HelpCircle, 
  AlertTriangle,
  Lightbulb,
  Compass,
  RefreshCw,
  BookOpen
} from "lucide-react";

interface ReportData {
  hours_consumed: number;
  insights_extracted: number;
  actions_completed: number;
  vocabulary_mastered: number;
  most_recurring_themes: string[];
  blind_spots: string[];
  recent_activity: any[];
}

export default function ReportPage() {
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [reviewedCount, setReviewedCount] = useState(0);

  const fetchReport = async () => {
    try {
      const res = await fetch(`${getApiUrl()}/api/report`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      } else {
        throw new Error("Failed to fetch");
      }
    } catch (err) {
      console.warn("Backend API not reachable. Mocking Weekly Report.");
      setData({
        hours_consumed: 18.5,
        insights_extracted: 142,
        actions_completed: 24,
        vocabulary_mastered: 48,
        most_recurring_themes: ["Compounding Systems", "Leverage and Scale", "Network Effects"],
        blind_spots: [
          "Short-term trade-offs of structural transitions",
          "Risk of choice over-analysis when evaluating options"
        ],
        recent_activity: []
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#060609]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-[#8b5cf6] animate-spin" />
          <p className="text-sm text-gray-400">Compiling Intelligence Report...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-5xl mx-auto w-full">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white text-gradient">
            Weekly Intelligence Report
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Analyzing your learning habits, vocabulary expansion, and conceptual blindspots.
          </p>
        </div>
        <button 
          onClick={() => {
            setLoading(true);
            fetchReport();
          }}
          className="p-2.5 rounded-xl glass-panel text-gray-400 hover:text-white"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: "Hours Consumed", value: `${data.hours_consumed}h`, detail: "+2.4h this week", icon: Clock },
          { label: "Insights Extracted", value: data.insights_extracted, detail: "+18 this week", icon: TrendingUp },
          { label: "Actions Completed", value: `${data.actions_completed} logged`, detail: "82% success rate", icon: CheckSquare },
          { label: "Vocabulary Mastered", value: data.vocabulary_mastered, detail: "15 new words logged", icon: BookOpen }
        ].map((stat, idx) => (
          <div key={idx} className="glass-panel p-6 rounded-2xl glow-purple flex flex-col justify-between">
            <div className="flex justify-between items-start">
              <span className="text-xs font-semibold text-gray-400 tracking-wider uppercase">{stat.label}</span>
              <stat.icon className="w-4 h-4 text-[#8b5cf6]" />
            </div>
            <div className="mt-4">
              <span className="text-2xl font-bold text-white block">{stat.value}</span>
              <span className="text-[10px] font-semibold text-emerald-400 mt-1 block">{stat.detail}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Analysis Block */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Left 2 Cols: Insights, Themes & Gaps */}
        <div className="md:col-span-2 space-y-6">
          {/* Spaced Repetition Panel */}
          <div className="glass-panel p-6 rounded-2xl glow-purple bg-gradient-to-tr from-[rgba(139,92,246,0.03)] to-transparent">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Compass className="w-5 h-5 text-[#8b5cf6]" />
              Spaced Repetition: Daily Review List
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Revisit these concepts to keep them fresh in your working memory.
            </p>

            <div className="mt-6 space-y-4">
              {[
                { title: "Network Effects", context: "How products become exponentially more valuable as users grow.", date: "Ingested 14 days ago" },
                { title: "Bayesian Reasoning", context: "Continuously updating probability predictions based on incoming evidence.", date: "Ingested 7 days ago" },
                { title: "First Principles Design", context: "Deconstructing systems down to fundamental truths and building up from there.", date: "Ingested 2 days ago" }
              ].map((item, idx) => {
                const isReviewed = idx < reviewedCount;
                return (
                  <div 
                    key={idx} 
                    className={`p-4 rounded-xl border transition-all duration-300 flex justify-between items-center ${
                      isReviewed 
                        ? "bg-[rgba(16,185,129,0.02)] border-emerald-500/20 opacity-60" 
                        : "bg-[rgba(255,255,255,0.01)] border-[rgba(255,255,255,0.03)]"
                    }`}
                  >
                    <div>
                      <h4 className={`text-sm font-semibold ${isReviewed ? "text-gray-500 line-through" : "text-white"}`}>
                        {item.title}
                      </h4>
                      <p className="text-xs text-gray-400 mt-1 max-w-md">{item.context}</p>
                      <span className="text-[10px] text-gray-500 mt-2 block">{item.date}</span>
                    </div>
                    {!isReviewed && (
                      <button
                        onClick={() => setReviewedCount(prev => prev + 1)}
                        className="px-3 py-1.5 bg-[rgba(139,92,246,0.1)] text-[#8b5cf6] border border-[rgba(139,92,246,0.2)] rounded-lg text-xs font-semibold hover:bg-[rgba(139,92,246,0.15)] transition-colors"
                      >
                        Mark Reviewed
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Learning Gaps */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-cyan-400" />
              Identified Learning Gaps
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Knowledge gaps detected by your Ingestion and Personal Intelligence logs.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              {[
                { domain: "Economics & Game Theory", reason: "Multiple insights mention incentives, but game theory models are rarely logged.", suggestion: "Add articles on Nash Equilibria." },
                { domain: "AI Scaling & Constraints", reason: "Frequent discussions on AI agents, but resource scaling limits are missed.", suggestion: "Ingest latest papers from DeepMind." }
              ].map((gap, idx) => (
                <div key={idx} className="bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.03)] p-4 rounded-xl space-y-2">
                  <h4 className="text-sm font-semibold text-white">{gap.domain}</h4>
                  <p className="text-xs text-gray-400 leading-relaxed">{gap.reason}</p>
                  <p className="text-[11px] text-[#06b6d4] font-semibold flex items-center gap-1 mt-2">
                    <span>Recommendation:</span> {gap.suggestion}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 1 Col: Themes & Blind Spots */}
        <div className="space-y-6">
          {/* Recurring Themes */}
          <div className="glass-panel p-6 rounded-2xl glow-cyan">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
              Recurring Themes
            </h3>
            <div className="mt-4 space-y-3">
              {data.most_recurring_themes.map((theme, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.03)] rounded-xl">
                  <span className="text-xs text-white font-medium">{theme}</span>
                  <span className="text-[10px] font-bold text-cyan-400 bg-[rgba(6,182,212,0.1)] px-2 py-0.5 rounded">
                    Core Pillar
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Blind Spots */}
          <div className="glass-panel p-6 rounded-2xl border-red-500/20 bg-gradient-to-b from-[rgba(239,68,68,0.02)] to-transparent">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              Cognitive Blind Spots
            </h3>
            <p className="text-xs text-gray-400 mt-1">
              Challenged perspectives surfaced by the Contrarian Agent:
            </p>
            <div className="mt-4 space-y-3">
              {data.blind_spots.map((spot, idx) => (
                <div key={idx} className="p-3 bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.03)] rounded-xl">
                  <p className="text-xs text-gray-300 leading-relaxed font-medium">
                    &ldquo;{spot}&rdquo;
                  </p>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}