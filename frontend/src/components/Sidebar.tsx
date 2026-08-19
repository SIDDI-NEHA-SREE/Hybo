"use client";

import React, { useState } from "react";

interface KnowledgeSource {
  url: string;
  status: "processing" | "success" | "failed";
  message?: string;
  pages_count: number;
  updated_at: string;
}

interface SidebarProps {
  sources: KnowledgeSource[];
  onAddSource: (url: string) => Promise<void>;
  onDeleteSource: (url: string) => Promise<void>;
}

export default function Sidebar({ sources, onAddSource, onDeleteSource }: SidebarProps) {
  const [urlInput, setUrlInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const futureModules = [
    {
      title: "GIS 3D Twin Map",
      description: "Visual 3D model overlays mapping city lines, ward borders, and utility layouts.",
      icon: "🗺️",
      badge: "Phase 3"
    },
    {
      title: "IoT Stream Telemetry",
      description: "Real-time feeds mapping municipal water levels, local air quality, and traffic indices.",
      icon: "📶",
      badge: "Phase 3"
    },
    {
      title: "Municipal AI Agents",
      description: "Dedicated sub-agents representing GHMC, HMDA, TSRTC, and emergency portals.",
      icon: "🤖",
      badge: "Phase 2"
    }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const targetUrl = urlInput.trim();
    if (!targetUrl) return;

    setIsSubmitting(true);
    setErrorMsg("");

    try {
      await onAddSource(targetUrl);
      setUrlInput("");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to add website source.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDisplayUrl = (url: string) => {
    try {
      const parsed = new URL(url);
      const pathname = parsed.pathname === "/" ? "" : parsed.pathname;
      return `${parsed.hostname}${pathname}`;
    } catch (e) {
      return url;
    }
  };

  return (
    <aside className="w-80 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 flex flex-col gap-6 hidden md:flex transition-colors overflow-y-auto">
      {/* Platform Scope */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">
          Platform Scope
        </h3>
        <div className="bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl p-4 text-xs text-slate-600 dark:text-slate-400 leading-relaxed shadow-sm">
          <strong className="text-slate-800 dark:text-slate-200 block mb-1">🎯 Hyderabad & TS</strong>
          HYBO Assistant answers questions strictly regarding local government schemes, circulars, tourist spots, transport, history, and emergency services in Hyderabad and Telangana.
        </div>
      </div>

      {/* Website Knowledge Section */}
      <div className="border-t border-slate-100 dark:border-slate-800 pt-5">
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">
          Website Knowledge
        </h3>
        
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="flex flex-col gap-2">
            <input
              type="text"
              placeholder="Enter Website URL (https://...)"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              disabled={isSubmitting}
              className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              aria-label="Website Knowledge URL"
            />
            <button
              type="submit"
              disabled={isSubmitting || !urlInput.trim()}
              className="w-full py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-colors cursor-pointer disabled:opacity-50 flex items-center justify-center gap-1.5 shadow-sm"
            >
              {isSubmitting ? (
                <>
                  <span className="w-3.5 h-3.5 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                  Processing...
                </>
              ) : (
                "Add Website 🌐"
              )}
            </button>
          </div>
          {errorMsg && (
            <p className="text-[10px] font-semibold text-red-500 mt-2 bg-red-500/5 border border-red-500/10 rounded-lg p-2 leading-tight">
              ⚠️ {errorMsg}
            </p>
          )}
        </form>

        {/* Knowledge Sources List */}
        {sources.length > 0 && (
          <div className="space-y-2 mt-4">
            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-1">
              Knowledge Sources:
            </span>
            <div className="max-h-48 overflow-y-auto space-y-2 pr-1.5">
              {sources.map((src, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between gap-2.5 p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800/80 text-xs text-slate-700 dark:text-slate-300"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {src.status === "processing" ? (
                      <span className="w-3 h-3 rounded-full border border-blue-500/30 border-t-blue-500 animate-spin shrink-0"></span>
                    ) : src.status === "success" ? (
                      <span className="text-emerald-500 font-bold text-xs shrink-0" title={`${src.pages_count} pages indexed`}>✓</span>
                    ) : (
                      <span className="text-red-500 font-bold text-xs shrink-0" title={src.message || "Failed to load"}>⚠️</span>
                    )}
                    <span 
                      className="truncate font-medium text-[11px]" 
                      title={src.url}
                    >
                      {getDisplayUrl(src.url)}
                    </span>
                  </div>
                  
                  <button
                    onClick={() => onDeleteSource(src.url)}
                    className="p-1 text-slate-400 hover:text-red-500 dark:hover:text-red-400 cursor-pointer font-bold text-[10px] transition-colors shrink-0"
                    title="Remove website knowledge source"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Future Modules */}
      <div className="flex-1 flex flex-col gap-4 border-t border-slate-100 dark:border-slate-800 pt-5">
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-1">
          Future Modules
        </h3>
        <div className="flex flex-col gap-3">
          {futureModules.map((module, idx) => (
            <div
              key={idx}
              className="bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100 dark:border-slate-800 p-3.5 rounded-xl flex gap-3 items-start transition-all hover:translate-x-0.5"
            >
              <span className="text-xl p-1 bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-100 dark:border-slate-700">
                {module.icon}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center gap-2 mb-1">
                  <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                    {module.title}
                  </h4>
                  <span className="text-[8px] font-bold px-1.5 py-0.5 rounded bg-slate-200/50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 shrink-0">
                    {module.badge}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-normal">
                  {module.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-slate-100 dark:border-slate-800 pt-4 text-center">
        <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium">
          HYBO Digital Twin Platform v0.2.0
        </span>
      </div>
    </aside>
  );
}
