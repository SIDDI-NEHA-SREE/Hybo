"use client";

import React from "react";

export default function Sidebar() {
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

  return (
    <aside className="w-80 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 flex flex-col gap-6 hidden md:flex transition-colors overflow-y-auto">
      <div>
        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">
          Platform Scope
        </h3>
        <div className="bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl p-4 text-xs text-slate-600 dark:text-slate-400 leading-relaxed shadow-sm">
          <strong className="text-slate-800 dark:text-slate-200 block mb-1">🎯 Hyderabad & TS</strong>
          HYBO Assistant answers questions strictly regarding local government schemes, circulars, tourist spots, transport, history, and emergency services in Hyderabad and Telangana.
        </div>
      </div>

      <div className="flex-1 flex flex-col gap-4">
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
