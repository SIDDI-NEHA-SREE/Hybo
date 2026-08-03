"use client";

import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import ChatWindow, { Message } from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

export default function Home() {
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [language, setLanguage] = useState("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize theme Class on document element
  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const handleSend = (text: string) => {
    // Add user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    // Simulate response delay
    setTimeout(() => {
      setIsLoading(false);
      const lowerText = text.toLowerCase();

      // Check if it is local to Hyd / TS
      const isHyderabadOrTS = 
        lowerText.includes("hyderabad") || 
        lowerText.includes("telangana") || 
        lowerText.includes("charminar") || 
        lowerText.includes("biryani") ||
        lowerText.includes("ghmc") ||
        lowerText.includes("hmda") ||
        lowerText.includes("kcr") ||
        lowerText.includes("revanth") ||
        lowerText.includes("cyberabad") ||
        lowerText.includes("secunderabad") ||
        lowerText.includes("tsrtc") ||
        lowerText.includes("hospital") ||
        lowerText.includes("scheme") ||
        lowerText.includes("metro");

      let responseText = "";

      if (!isHyderabadOrTS) {
        responseText = "I specialize ONLY in Hyderabad and Telangana related topics. Please ask me about local welfare schemes, historical landmarks, transport routes, or emergency contacts within our state.";
      } else {
        responseText = `Thank you for asking about "${text}". This is a premium frontend streaming simulation. In subsequent phases, we will integrate FastAPI and AWS Bedrock (Claude 3.5 Sonnet) to retrieve live, accurate information directly from official sources without storing it locally.`;
      }

      // Stream simulation
      const botMsgId = `bot-${Date.now()}`;
      const words = responseText.split(" ");
      let currentWordIndex = 0;

      // Create empty bot bubble
      const initialBotMsg: Message = {
        id: botMsgId,
        sender: "assistant",
        text: "",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        isStreaming: true
      };

      setMessages((prev) => [...prev, initialBotMsg]);

      const interval = setInterval(() => {
        if (currentWordIndex < words.length) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === botMsgId
                ? { ...m, text: words.slice(0, currentWordIndex + 1).join(" ") }
                : m
            )
          );
          currentWordIndex++;
        } else {
          clearInterval(interval);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === botMsgId ? { ...m, isStreaming: false } : m
            )
          );
        }
      }, 70); // Typist speed
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors">
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        language={language}
        setLanguage={setLanguage}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col bg-slate-50/50 dark:bg-slate-900/40 relative">
          <ChatWindow
            messages={messages}
            onSuggestedClick={handleSend}
            isLoading={isLoading}
          />
          <ChatInput onSend={handleSend} isLoading={isLoading} />
        </main>
      </div>
    </div>
  );
}
