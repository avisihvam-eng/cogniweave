"use client";

import { useEffect, useState } from "react";
import { 
  Play, 
  BookOpen, 
  Youtube, 
  ExternalLink, 
  FileText, 
  Clock, 
  TrendingUp, 
  Award, 
  Star, 
  ChevronRight,
  RefreshCw,
  Plus
} from "lucide-react";
import Link from "next/link";

interface DocumentItem {
  id: string;
  title: string;
  speaker: string;
  date: string;
  duration: number;
  source: string;
  url: string;
  google_doc_link: string;
  personal_rating: number;
}

interface StatsReport {
  hours_consumed: number;
  insights_extracted: number;
  actions_completed: number;
  vocabulary_mastered: number;
}

export default function Dashboard() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [stats, setStats] = useState<StatsReport>({
    hours_consumed: 0,
    insights_extracted: 0,
    actions_completed: 0,
    vocabulary_mastered: 0
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const docsRes = await fetch("http://localhost:8000/api/documents");
      const reportRes = await fetch("http://localhost:8000/api/report");
      
      if (docsRes.ok && reportRes.ok) {
        const docsData = await docsRes.json();
        const reportData = await reportRes.json();
        setDocuments(docsData);
        setStats(reportData);
      } else {
        throw new Error("Failed to fetch");
      }
    } catch (err) {
      console.warn("Backend API not reachable. Using fallback mock data.");
      // Fallback Mock Data
      setDocuments([
        {
          id: "1",
          title: "How Great Founders Think - Charlie Munger & Naval Ravikant",
          speaker: "Naval Ravikant",
          date: new Date().toLocaleDateString(),
          duration: 3600,
          source: "YouTube",
          url: "https://www.youtube.com/watch?v=NavalMunger",
          google_doc_link: "#",
          personal_rating: 5
        },
        {
          id: "2",
          title: "Scaling Systems and Network Effects",
          speaker: "Keith Rabois",
          date: new Date().toLocaleDateString(),
          duration: 2700,
          source: "Podcast",
          url: "https://spotify.com/episode/ScalingSystems",
          google_doc_link: "#",
          personal_rating: 4
        },
        {
          id: "3",
          title: "First Principles Design in AI Architectures",
          speaker: "Demis Hassabis",
          date: new Date().toLocaleDateString(),
          duration: 4800,
          source: "Research Paper",
          url: "https://arxiv.org/abs/first-principles-ai",
          google_doc_link: "#",
          personal_rating: 5
        }
      ]);
      setStats({
        hours_consumed: 18.5,
        insights_extracted: 142,
        actions_completed: 24,
        vocabulary_mastered: 48
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRate = async (docId: string, currentRating: number) => {
    const nextRating = currentRating === 5 ? 1 : currentRating + 1;
    // Optimistic UI update
    setDocuments(prev => prev.map(d => d.id === docId ? { ...d, personal_rating: nextRating } : d));
    try {
      await fetch(`http://localhost:8000/api/documents/${docId}/rate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rating: nextRating })
      });
    } catch (e) {
      console.error("Failed to persist rating", e);
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source.toLowerCase()) {
      case "youtube":
        return <Youtube className="w-4 h-4 text-red-400" />;
      case "podcast":
        return <Play className="w-4 h-4 text-green-400" />;
      case "research paper":
      case "pdf":
        return <BookOpen className="w-4 h-4 text-cyan-400" />;
      default:
        return <FileText className="w-4 h-4 text-purple-400" />;
    }
  };

  const formatDuration = (sec: number) => {
    if (!sec) return "N/A";
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    return hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`;
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#060609]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-[#8b5cf6] animate-spin" />
          <p className="text-sm text-gray-400 font-medium">Syncing Knowledge Base...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
      {/* Dashboard Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white text-gradient">
            Knowledge Dashboard
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Your compounding wisdom archive. Review inputs and mental connections.
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => {
              setRefreshing(true);
              fetchDashboardData();
            }}
            className="p-3 rounded-xl glass-panel text-gray-400 hover:text-white transition-all duration-300"
            disabled={refreshing}
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          </button>
          <Link 
            href="/ingest"
            className="flex items-center gap-2 px-5 py-3 bg-[#8b5cf6] text-white rounded-xl text-sm font-semibold hover:bg-[#7c3aed] transition-all duration-300 glow-purple"
          >
            <Plus className="w-4 h-4" /> Ingest Content
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: "Hours Consumed", value: `${stats.hours_consumed} hrs`, icon: Clock, glow: "glow-purple" },
          { label: "Insights Extracted", value: stats.insights_extracted, icon: TrendingUp, glow: "glow-cyan" },
          { label: "Actions Generated", value: stats.actions_completed, icon: Award, glow: "glow-purple" },
          { label: "Vocabulary Mastered", value: stats.vocabulary_mastered, icon: BookOpen, glow: "glow-cyan" }
        ].map((item, idx) => (
          <div key={idx} className={`glass-panel p-6 rounded-2xl flex items-center justify-between transition-all duration-300 hover:scale-[1.02] ${item.glow}`}>
            <div>
              <span className="text-xs font-semibold text-gray-400 tracking-wider uppercase block">
                {item.label}
              </span>
              <span className="text-2xl font-bold text-white mt-1 block">
                {item.value}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.05)]">
              <item.icon className="w-5 h-5 text-[#8b5cf6]" />
            </div>
          </div>
        ))}
      </div>

      {/* Personal Takeaways spotlight */}
      <div className="glass-panel p-6 rounded-2xl glow-purple bg-gradient-to-r from-[rgba(139,92,246,0.05)] to-transparent">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#8b5cf6]"></span>
          Daily Spaced Repetition Spotlight
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Surfaced insights you might have forgotten. Revisit to boost retention.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.03)] p-5 rounded-xl">
            <span className="text-xs font-bold text-[#8b5cf6] uppercase tracking-wider">Insight worth remembering</span>
            <p className="text-sm text-white font-medium mt-2 leading-relaxed">
              &ldquo;Knowledge is a compounding asset. Small efforts daily creates massive divergence between linear and exponential curves.&rdquo;
            </p>
            <span className="text-[11px] text-gray-400 mt-3 block">&mdash; Naval Ravikant, How Great Founders Think</span>
          </div>

          <div className="bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.03)] p-5 rounded-xl flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold text-[#06b6d4] uppercase tracking-wider">Concrete Action Item</span>
              <p className="text-sm text-white font-medium mt-2 leading-relaxed">
                Allocate 2 hours this week to explore a completely new technical domain.
              </p>
            </div>
            <div className="mt-4 flex gap-4 text-[11px] text-gray-400">
              <span>Difficulty: Easy</span>
              <span>Impact: High</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recently Processed Section */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="px-6 py-5 border-b border-[rgba(255,255,255,0.04)] flex justify-between items-center">
          <h2 className="text-lg font-bold text-white">Recently Compiled Knowledge</h2>
          <span className="text-xs text-[#8b5cf6] font-semibold">{documents.length} items total</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[rgba(255,255,255,0.04)] text-xs text-gray-400 uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">Title</th>
                <th className="px-6 py-4 font-semibold">Source</th>
                <th className="px-6 py-4 font-semibold">Speaker</th>
                <th className="px-6 py-4 font-semibold">Duration</th>
                <th className="px-6 py-4 font-semibold">Rating</th>
                <th className="px-6 py-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[rgba(255,255,255,0.02)] text-sm text-gray-200">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-[rgba(255,255,255,0.01)] transition-colors duration-200">
                  <td className="px-6 py-4 font-medium text-white max-w-sm truncate">
                    {doc.title}
                  </td>
                  <td className="px-6 py-4">
                    <span className="flex items-center gap-1.5 capitalize text-xs text-gray-300">
                      {getSourceIcon(doc.source)}
                      {doc.source}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-300">{doc.speaker}</td>
                  <td className="px-6 py-4 text-gray-400">{formatDuration(doc.duration)}</td>
                  <td className="px-6 py-4">
                    <button 
                      onClick={() => handleRate(doc.id, doc.personal_rating)}
                      className="flex items-center gap-1 text-yellow-400 hover:scale-110 transition-transform"
                    >
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`w-3.5 h-3.5 ${i < doc.personal_rating ? "fill-yellow-400" : "text-gray-600"}`} 
                        />
                      ))}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      {doc.url && (
                        <a 
                          href={doc.url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="p-2 hover:bg-[rgba(255,255,255,0.03)] rounded-lg text-gray-400 hover:text-white transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                      <a 
                        href={doc.google_doc_link}
                        target="_blank"
                        rel="noreferrer" 
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-[rgba(139,92,246,0.1)] text-[#8b5cf6] border border-[rgba(139,92,246,0.2)] rounded-lg text-xs font-semibold hover:bg-[rgba(139,92,246,0.15)] transition-colors"
                      >
                        Google Doc <ChevronRight className="w-3 h-3" />
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
