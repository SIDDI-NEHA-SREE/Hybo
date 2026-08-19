"use client";

import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import ChatWindow, { Message } from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import AuthModal from "../components/AuthModal";
import ProfileModal from "../components/ProfileModal";
import { supabase } from "../utils/supabaseClient";

interface KnowledgeSource {
  url: string;
  status: "processing" | "success" | "failed";
  message?: string;
  pages_count: number;
  updated_at: string;
}

export default function Home() {
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [language, setLanguage] = useState("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Auth states
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // RAG / Knowledge states
  const [sources, setSources] = useState<KnowledgeSource[]>([]);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Initialize theme class on document element
  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  // Load token and user session on mount
  useEffect(() => {
    const initAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        setToken(session.access_token);
        fetchUserProfile(session.access_token);
      }
    };
    initAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session) {
        setToken(session.access_token);
        fetchUserProfile(session.access_token);
      } else if (event === "SIGNED_OUT") {
        setToken(null);
        setUser(null);
      }
    });

    // Fetch knowledge sources
    fetchSources();

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Poll status periodically if any source is in "processing" status
  useEffect(() => {
    const hasProcessing = sources.some((s) => s.status === "processing");
    if (hasProcessing) {
      const interval = setInterval(() => {
        fetchSources();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [sources]);

  const fetchUserProfile = async (authToken: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        if (data.authenticated && data.user) {
          setUser(data.user);
        } else {
          handleLogout();
        }
      } else {
        handleLogout();
      }
    } catch (err) {
      console.error("Session verification failed:", err);
      handleLogout();
    }
  };

  const handleAuthSuccess = (newToken: string, loggedInUser: any) => {
    setToken(newToken);
    setUser(loggedInUser);
    
    // Add a welcome bot message automatically when user logs in
    const welcomeMsg: Message = {
      id: `bot-welcome-${Date.now()}`,
      sender: "assistant",
      text: `Hello ${loggedInUser.name}! Welcome to HYBO Assistant. You are now logged in. How can I help you today?`,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
    setMessages((prev) => [...prev, welcomeMsg]);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setToken(null);
    setUser(null);
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  // --- RAG Source Handlers ---

  const fetchSources = async () => {
    try {
      const response = await fetch(`${API_URL}/api/knowledge/sources`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.sources) {
          setSources(data.sources);
        }
      }
    } catch (err) {
      console.error("Failed to fetch knowledge sources:", err);
    }
  };

  const handleAddSource = async (url: string) => {
    const response = await fetch(`${API_URL}/api/knowledge/url`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to add website source.");
    }
    
    // Instantly refresh list to show "processing" state
    await fetchSources();
  };

  const handleDeleteSource = async (url: string) => {
    const response = await fetch(`${API_URL}/api/knowledge/url?url=${encodeURIComponent(url)}`, {
      method: "DELETE",
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Failed to delete website source.");
    }

    // Refresh list
    await fetchSources();
  };

  const handleSend = async (text: string) => {
    // Add user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    let responseText = "";
    let citedSources: string[] = [];

    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      // Send query to FastAPI chat interaction endpoint
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          message: text,
          language: language,
          session_id: "default-session"
        })
      });

      setIsLoading(false);

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.reply) {
          responseText = data.reply;
          citedSources = data.sources || [];
        } else {
          responseText = data.message || "The AI assistant service returned an error.";
        }
      } else {
        throw new Error("HTTP error on chat endpoint");
      }
    } catch (err) {
      console.log("FastAPI backend is offline or failed. Falling back to local frontend simulation:", err);
      setIsLoading(false);
      
      // Fallback local simulation logic
      const lowerText = text.toLowerCase();
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

      if (!isHyderabadOrTS) {
        responseText = "I specialize ONLY in Hyderabad and Telangana related topics. Please ask me about local welfare schemes, historical landmarks, transport routes, or emergency contacts within our state.";
      } else {
        responseText = `Thank you for asking about "${text}". This is a premium frontend streaming simulation. In subsequent phases, we will integrate FastAPI and AWS Bedrock (Claude 3.5 Sonnet) to retrieve live, accurate information directly from official sources without storing it locally.`;
      }
    }

    // Stream simulation for output typing animation
    const botMsgId = `bot-${Date.now()}`;
    const words = responseText.split(" ");
    let currentWordIndex = 0;

    // Create empty bot bubble
    const initialBotMsg: Message = {
      id: botMsgId,
      sender: "assistant",
      text: "",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      isStreaming: true,
      sources: citedSources.length > 0 ? citedSources : undefined
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
    }, 45); // Adjust typing speed
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors">
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        language={language}
        setLanguage={setLanguage}
        user={user}
        onOpenLogin={() => setIsLoginOpen(true)}
        onOpenProfile={() => setIsProfileOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          sources={sources}
          onAddSource={handleAddSource}
          onDeleteSource={handleDeleteSource}
        />
        <main className="flex-1 flex flex-col bg-slate-50/50 dark:bg-slate-900/40 relative">
          <ChatWindow
            messages={messages}
            onSuggestedClick={handleSend}
            isLoading={isLoading}
            userName={user?.name}
          />
          <ChatInput onSend={handleSend} isLoading={isLoading} />
        </main>
      </div>

      {/* Modals */}
      <AuthModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        user={user}
        token={token}
        onUpdateUser={(updated) => setUser(updated)}
        onLogout={handleLogout}
      />
    </div>
  );
}
