"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  UploadCloud, 
  Search, 
  Network, 
  FileText, 
  Settings, 
  BrainCircuit 
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Compile", href: "/ingest", icon: UploadCloud },
    { name: "Semantic Search", href: "/search", icon: Search },
    { name: "Knowledge Graph", href: "/graph", icon: Network },
    { name: "Weekly Report", href: "/report", icon: FileText },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-[rgba(255,255,255,0.05)] bg-[#09090d] flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-[rgba(255,255,255,0.04)]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center glow-purple">
          <BrainCircuit className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-semibold text-white tracking-wider">ANTIGRAVITY</span>
          <span className="text-[10px] block text-gradient font-bold tracking-widest -mt-1">KNOWLEDGE COMPILER</span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ${
                isActive 
                  ? "bg-gradient-to-r from-[rgba(139,92,246,0.15)] to-[rgba(6,182,212,0.05)] border border-[rgba(139,92,246,0.2)] text-white" 
                  : "text-[#9ca3af] hover:text-white hover:bg-[rgba(255,255,255,0.02)] border border-transparent"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-[#8b5cf6]" : "text-[#6b7280] group-hover:text-white"}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User Status Bar */}
      <div className="p-4 border-t border-[rgba(255,255,255,0.05)] bg-[#07070a]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#8b5cf6] to-[#06b6d4] flex items-center justify-center text-xs font-semibold text-white">
            AS
          </div>
          <div>
            <p className="text-xs font-medium text-white">Avinash Shukla</p>
            <span className="text-[10px] text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Workspace Linked
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
