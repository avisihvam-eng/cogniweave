"use client";

import { useState, useEffect } from "react";
import { 
  Settings, 
  Key, 
  User, 
  FolderGit, 
  CheckCircle2, 
  RefreshCw, 
  Sparkles,
  Save,
  HelpCircle
} from "lucide-react";

export default function SettingsPage() {
  // Config state
  const [geminiKey, setGeminiKey] = useState("");
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  
  // Profile state
  const [career, setCareer] = useState("Recruiter learning AI");
  const [goals, setGoals] = useState("Understand AI agents and organizational efficiency");
  const [interests, setInterests] = useState("AI, Systems thinking, Decision making");
  
  // Connection states
  const [googleLinked, setGoogleLinked] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Load from local storage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      setGeminiKey(localStorage.getItem("GEMINI_API_KEY") || "");
      setClientId(localStorage.getItem("GOOGLE_CLIENT_ID") || "");
      setClientSecret(localStorage.getItem("GOOGLE_CLIENT_SECRET") || "");
      
      const profile = JSON.parse(localStorage.getItem("USER_PROFILE") || "{}");
      if (profile.career) setCareer(profile.career);
      if (profile.goals) setGoals(profile.goals);
      if (profile.interests) setInterests(profile.interests);
    }
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);

    setTimeout(() => {
      if (typeof window !== "undefined") {
        localStorage.setItem("GEMINI_API_KEY", geminiKey);
        localStorage.setItem("GOOGLE_CLIENT_ID", clientId);
        localStorage.setItem("GOOGLE_CLIENT_SECRET", clientSecret);
        
        localStorage.setItem("USER_PROFILE", JSON.stringify({
          career,
          goals,
          interests
        }));
      }
      setSaving(false);
      setSaved(true);
    }, 1000);
  };

  const handleGoogleLink = () => {
    setGoogleLinked(!googleLinked);
  };

  return (
    <div className="p-8 space-y-8 max-w-3xl mx-auto w-full">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white text-gradient">
          System Settings
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Configure external API keys, Google Workspace linkages, and personalized intelligence profiles.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* API Credentials */}
        <div className="glass-panel p-6 rounded-2xl glow-purple space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <Key className="w-4 h-4 text-[#8b5cf6]" />
            API & Model Credentials
          </h3>
          
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Gemini API Key
              </label>
              <input
                type="password"
                placeholder="AIzaSy..."
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.05)] rounded-xl px-4 py-3 mt-2 text-sm text-white focus:outline-none focus:border-[#8b5cf6] transition-colors"
              />
              <p className="text-[10px] text-gray-500 mt-1">Required to run the 12 deep-reasoning agents and embedding indexing.</p>
            </div>
          </div>
        </div>

        {/* Personalization Intelligence */}
        <div className="glass-panel p-6 rounded-2xl glow-cyan space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <User className="w-4 h-4 text-cyan-400" />
            Personal Intelligence Profile
          </h3>
          <p className="text-xs text-gray-400">
            Tell the system about your career and learning goals. The Personal Intelligence Agent uses this to highlight relevant domains and ignore irrelevant topics.
          </p>

          <div className="space-y-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">Career Domain / Title</label>
              <input
                type="text"
                placeholder="e.g. Recruiter learning AI, Startup Founder, Research Scientist"
                value={career}
                onChange={(e) => setCareer(e.target.value)}
                className="w-full bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.05)] rounded-xl px-4 py-3 mt-2 text-sm text-white focus:outline-none focus:border-[#8b5cf6]"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">Current Learning Goals</label>
              <input
                type="text"
                placeholder="e.g. Understand AI systems, Master systems thinking"
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                className="w-full bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.05)] rounded-xl px-4 py-3 mt-2 text-sm text-white focus:outline-none focus:border-[#8b5cf6]"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">Target Focus Topics</label>
              <input
                type="text"
                placeholder="e.g. AI, Recuriting, Decision-making, Leveraged Growth"
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                className="w-full bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.05)] rounded-xl px-4 py-3 mt-2 text-sm text-white focus:outline-none focus:border-[#8b5cf6]"
              />
            </div>
          </div>
        </div>

        {/* Google Workspace Integration */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <FolderGit className="w-4 h-4 text-[#8b5cf6]" />
            Google Workspace Integration
          </h3>

          <div className="p-4 rounded-xl bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.03)] flex justify-between items-center">
            <div>
              <span className="text-xs font-bold text-white">Google OAuth Linkage</span>
              <span className="text-[10px] text-gray-400 block mt-1">
                {googleLinked ? "Connected as user@domain.com" : "Not connected. Running in Local Workspace Mode."}
              </span>
            </div>
            <button
              type="button"
              onClick={handleGoogleLink}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all duration-300 ${
                googleLinked 
                  ? "bg-[rgba(239,68,68,0.1)] border-red-500/20 text-red-400 hover:bg-[rgba(239,68,68,0.15)]" 
                  : "bg-[#8b5cf6] border-[#8b5cf6] text-white hover:bg-[#7c3aed]"
              }`}
            >
              {googleLinked ? "Disconnect Drive" : "Connect Google Drive"}
            </button>
          </div>

          <div className="space-y-4 border-t border-[rgba(255,255,255,0.04)] pt-4">
            <span className="text-xs font-bold text-gray-400 block">Google Cloud OAuth Credentials</span>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider">OAuth Client ID</label>
                <input
                  type="text"
                  placeholder="xxxx-yyyy.apps.googleusercontent.com"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  className="w-full bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.04)] rounded-lg px-3 py-2 mt-1 text-xs text-white focus:outline-none focus:border-[#8b5cf6]"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider">OAuth Client Secret</label>
                <input
                  type="password"
                  placeholder="GOCSPX-zzzz"
                  value={clientSecret}
                  onChange={(e) => setClientSecret(e.target.value)}
                  className="w-full bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.04)] rounded-lg px-3 py-2 mt-1 text-xs text-white focus:outline-none focus:border-[#8b5cf6]"
                />
              </div>
            </div>
            <p className="text-[10px] text-gray-500">Provide these keys if you want to run Drive and Sheets synchronization under your custom Google Developer Console project.</p>
          </div>
        </div>

        {/* Submit Actions */}
        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-3 bg-[#8b5cf6] text-white rounded-xl text-sm font-semibold hover:bg-[#7c3aed] transition-all duration-300 disabled:bg-gray-700 glow-purple"
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Saving Configurations...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" /> Save Settings
              </>
            )}
          </button>
          {saved && (
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> System credentials saved successfully!
            </span>
          )}
        </div>
      </form>
    </div>
  );
}
