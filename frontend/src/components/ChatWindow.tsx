"use client";

import React, { useRef, useEffect } from "react";

export interface Message {
  id: string;
  sender: "user" | "assistant";
  text: string;
  time: string;
  isStreaming?: boolean;
}

interface ChatWindowProps {
  messages: Message[];
  onSuggestedClick: (question: string) => void;
  isLoading: boolean;
}

export default function ChatWindow({ messages, onSuggestedClick, isLoading }: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const suggestions = [
    "Tell me about the TS Rythu Bandhu scheme",
    "What are the visiting hours of Golconda Fort?",
    "Where is the nearest government area hospital?",
    "How do I apply for a GHMC birth certificate?"
  ];

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8 flex flex-col gap-6">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col justify-center items-center max-w-xl mx-auto text-center gap-6 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-amber-600 flex items-center justify-center text-3xl shadow-xl shadow-blue-500/10">
            🏛️
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">
              HYBO Assistant
            </h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
              Ask anything about Telangana schemes, Hyderabad history, metro routes, government offices, or hospital contacts.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-4">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => onSuggestedClick(s)}
                className="bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-700 dark:text-slate-300 rounded-xl p-4 text-xs font-semibold text-left transition-all shadow-sm cursor-pointer hover:-translate-y-0.5"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-6 max-w-3xl w-full mx-auto">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col gap-1 max-w-[85%] ${
                msg.sender === "user" ? "self-end items-end" : "self-start items-start"
              }`}
            >
              <div
                className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm transition-all ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
                {msg.isStreaming && (
                  <span className="inline-block w-1.5 h-4 ml-1 bg-current animate-pulse align-middle" />
                )}
              </div>
              <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium px-1">
                {msg.time}
              </span>
            </div>
          ))}

          {/* Loading / Typing indicator */}
          {isLoading && (
            <div className="flex flex-col gap-1 self-start items-start max-w-[85%] animate-pulse">
              <div className="px-4 py-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none flex items-center gap-1.5 h-10">
                <span className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-600 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-600 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-600 rounded-full animate-bounce" />
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      )}
    </div>
  );
}
