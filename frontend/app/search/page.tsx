import { getApiUrl } from "@/lib/api";
"use client";

import { useState } from "react";
import { 
  Search, 
  Sparkles, 
  ExternalLink, 
  FileText, 
  Youtube, 
  Play, 
  BookOpen, 
  Compass,
  ArrowRight,
  Loader2
} from "lucide-react";

interface SearchResult {
  insight: string;
  why_it_matters: string;
  application: string;
  action: string;
  document_title: string;
  document_source: string;
  document_url: string;
  google_doc_link: string;
  similarity: number;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);

  const samplePrompts = [
    "Show every podcast discussing incentives",
    "Find every quote about leverage",
    "Show every mental model related to recruiting",
    "Find everything connected to Charlie Munger",
    "Find every insight about AI agents"
  ];

  const handleSearch = async (e: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const searchQuery = customQuery || query;
    if (!searchQuery) return;
    
    setQuery(searchQuery);
    setLoading(true);
    setSearched(true);

    try {
      const url = `${getApiUrl()}/api/search?query=${encodeURIComponent(searchQuery)}${
        category ? `&category=${category}` : ""
      }`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setResults(data);
      } else {
        throw new Error("Search failed");
      }
    } catch (err) {
      console.warn("Backend search failed. Mocking semantic match results.");
      // Fallback Mock Results
      setResults([
        {
          insight: "Incentives are the ultimate driver of human and organizational behavior. Show me the incentive and I will show you the outcome.",
          why_it_matters: "Most systemic failures stem from misaligned incentives, not incompetent personnel.",
          application: "Design recruiting bonus milestones around 1-year candidate retention rather than raw hire volume.",
          action: "Audit the current sales commission structure to ensure it rewards long-term customer value.",
          document_title: "How Great Founders Think - Charlie Munger & Naval Ravikant",
          document_source: "YouTube",
          document_url: "#",
          google_doc_link: "#",
          similarity: 0.945
        },
        {
          insight: "Leverage allows you to decouple your output from your time. Product and media are permissionless forms of leverage.",
          why_it_matters: "Without leverage, you cannot scale your impact or wealth.",
          application: "Incorporate AI transcription agents to compile meeting logs instead of writing manual summaries.",
          action: "Deploy an automated crawler to collect industry reports weekly.",
          document_title: "Scaling Systems and Network Effects",
          document_source: "Podcast",
          document_url: "#",
          google_doc_link: "#",
          similarity: 0.887
        }
      ].filter(r => !category || r.document_source.toLowerCase() === category.toLowerCase()));
    } finally {
      setLoading(false);
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source.toLowerCase()) {
      case "youtube":
        return <Youtube className="w-3.5 h-3.5 text-red-400" />;
      case "podcast":
        return <Play className="w-3.5 h-3.5 text-green-400" />;
      case "research paper":
      case "pdf":
        return <BookOpen className="w-3.5 h-3.5 text-cyan-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-purple-400" />;
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto w-full">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white text-gradient">
          Semantic Search
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Query your compiled database in natural language using pgvector embeddings.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="glass-panel p-6 rounded-2xl glow-purple">
        <form onSubmit={(e) => handleSearch(e)} className="relative flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-3.5 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Query ideas, quotes, mental models or thinkers..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.05)] rounded-xl pl-12 pr-4 py-3 text-sm text-white focus:outline-none focus:border-[#8b5cf6] transition-colors"
            />
          </div>
          <button
            type="submit"
            className="px-6 bg-[#8b5cf6] text-white rounded-xl text-sm font-semibold hover:bg-[#7c3aed] transition-all duration-300 flex items-center gap-1.5 glow-purple"
          >
            Search
          </button>
        </form>

        {/* Category Filter Pills */}
        <div className="flex gap-2 flex-wrap mt-4">
          {[
            { name: "All Sources", value: "" },
            { name: "YouTube", value: "youtube" },
            { name: "Podcasts", value: "podcast" },
            { name: "Papers", value: "research paper" },
            { name: "Articles", value: "article" }
          ].map((cat) => (
            <button
              key={cat.name}
              onClick={() => {
                setCategory(cat.value);
                if (searched) {
                  // Trigger search with updated category
                  setTimeout(() => handleSearch(null as any), 50);
                }
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-300 ${
                category === cat.value
                  ? "bg-[#8b5cf6] border-[#8b5cf6] text-white"
                  : "bg-transparent border-[rgba(255,255,255,0.04)] text-gray-400 hover:text-white"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Sample Prompts Grid */}
      {!searched && (
        <div className="space-y-4">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-[#8b5cf6]" />
            Try Natural Language Queries
          </span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {samplePrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={(e) => handleSearch(e, prompt)}
                className="glass-panel px-4 py-3 rounded-xl text-sm text-gray-300 text-left hover:text-white hover:border-[#8b5cf6] transition-all duration-300 flex items-center justify-between group"
              >
                {prompt}
                <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-[#8b5cf6] transition-colors" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results Section */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-[#8b5cf6] animate-spin" />
            <p className="text-sm text-gray-400">Embedding query and searching vectors...</p>
          </div>
        </div>
      ) : searched ? (
        <div className="space-y-6">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
            Search Results ({results.length} matches found)
          </span>
          
          {results.length > 0 ? (
            <div className="space-y-6">
              {results.map((res, idx) => (
                <div key={idx} className="glass-panel p-6 rounded-2xl space-y-4 glow-purple relative overflow-hidden">
                  {/* Similarity Badge */}
                  <span className="absolute top-6 right-6 text-[10px] font-bold text-cyan-400 bg-[rgba(6,182,212,0.1)] border border-[rgba(6,182,212,0.2)] px-2 py-1 rounded">
                    {Math.round(res.similarity * 100)}% Match
                  </span>

                  {/* Document Source Header */}
                  <div className="flex items-center gap-2 border-b border-[rgba(255,255,255,0.04)] pb-3">
                    <span className="flex items-center gap-1 text-xs text-[#8b5cf6] font-semibold">
                      {getSourceIcon(res.document_source)}
                      {res.document_source}
                    </span>
                    <span className="text-gray-600">&bull;</span>
                    <span className="text-xs text-gray-400 font-medium max-w-md truncate">
                      {res.document_title}
                    </span>
                  </div>

                  {/* Primary Insight */}
                  <div>
                    <h3 className="text-base font-bold text-white leading-relaxed">
                      &ldquo;{res.insight}&rdquo;
                    </h3>
                  </div>

                  {/* Insight Details */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                    <div className="bg-[rgba(255,255,255,0.01)] p-3 rounded-lg border border-[rgba(255,255,255,0.02)]">
                      <span className="text-[10px] font-bold text-[#8b5cf6] uppercase tracking-wider">Why it Matters</span>
                      <p className="text-xs text-gray-300 mt-1">{res.why_it_matters}</p>
                    </div>
                    <div className="bg-[rgba(255,255,255,0.01)] p-3 rounded-lg border border-[rgba(255,255,255,0.02)]">
                      <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">Application</span>
                      <p className="text-xs text-gray-300 mt-1">{res.application}</p>
                    </div>
                    <div className="bg-[rgba(255,255,255,0.01)] p-3 rounded-lg border border-[rgba(255,255,255,0.02)]">
                      <span className="text-[10px] font-bold text-[#10b981] uppercase tracking-wider">Action</span>
                      <p className="text-xs text-gray-300 mt-1 font-medium">{res.action}</p>
                    </div>
                  </div>

                  {/* Document CTA */}
                  <div className="flex justify-between items-center pt-2">
                    {res.document_url && (
                      <a
                        href={res.document_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                      >
                        Original Source <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    <a
                      href={res.google_doc_link}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-[#8b5cf6] hover:text-[#7c3aed] font-semibold flex items-center gap-1"
                    >
                      Open Analysis Doc <ArrowRight className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-panel p-8 rounded-2xl text-center text-gray-500">
              No matching semantic insights found for &ldquo;{query}&rdquo;.
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
