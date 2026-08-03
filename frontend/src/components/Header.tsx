"use client";

import React from "react";

interface HeaderProps {
  theme: "light" | "dark";
  toggleTheme: () => void;
  language: string;
  setLanguage: (lang: string) => void;
}

export default function Header({ theme, toggleTheme, language, setLanguage }: HeaderProps) {
  return (
    <header className="border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-950/50 backdrop-blur-md px-6 py-4 flex justify-between items-center sticky top-0 z-50 transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-amber-600 flex items-center justify-center text-xl shadow-lg shadow-blue-500/10">
          🏛️
        </div>
        <div className="flex flex-col">
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-amber-600 dark:from-blue-400 dark:to-amber-400 bg-clip-text text-transparent tracking-tight">
            HYBO
          </span>
          <span className="text-[10px] font-bold tracking-widest text-slate-500 dark:text-slate-400 uppercase">
            City InsideOut
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Language Picker */}
        <div className="relative">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="appearance-none bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer font-medium"
            aria-label="Select Language"
          >
            <option value="en">English</option>
            <option value="te">తెలుగు (Telugu)</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="ur">اردو (Urdu)</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-500">
            ▼
          </div>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-all"
          aria-label={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
        >
          {theme === "light" ? "🌙" : "☀️"}
        </button>

        <div className="px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 hidden sm:inline-block">
          Active
        </div>
      </div>
    </header>
  );
}
