"use client";

import React, { useState } from "react";
import { supabase } from "../utils/supabaseClient";

interface UserProfile {
  id: string;
  email: string;
  phone_number?: string;
  name: string;
  role: string;
  created_at: string;
}

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (token: string, user: any) => void;
}

export default function AuthModal({ isOpen, onClose, onAuthSuccess }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [infoMessage, setInfoMessage] = useState("");

  if (!isOpen) return null;

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) return;

    setIsLoading(true);
    setErrorMessage("");
    setInfoMessage("");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      if (mode === "signup") {
        // 1. Sign up with Supabase Auth
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password: password,
          options: {
            data: {
              name: name.trim() || "Citizen User",
            },
          },
        });

        if (error) throw error;
        if (!data.user) throw new Error("Signup failed. Please try again.");

        // Check if email confirmation is required
        if (data.session) {
          // Sync profile to backend PostgreSQL
          const syncResponse = await fetch(`${apiUrl}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${data.session.access_token}`,
            },
          });
          
          if (!syncResponse.ok) {
            throw new Error("Could not sync profile with database.");
          }
          
          const syncData = await syncResponse.json();
          onAuthSuccess(data.session.access_token, syncData.user);
          onClose();
          resetForm();
        } else {
          setInfoMessage("Registration successful! Please check your email to verify your account.");
        }
      } else {
        // 2. Sign in with Supabase Auth
        const { data, error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password: password,
        });

        if (error) throw error;
        if (!data.session) throw new Error("Login failed. No session returned.");

        // Sync and get profile from backend PostgreSQL
        const syncResponse = await fetch(`${apiUrl}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${data.session.access_token}`,
          },
        });

        if (!syncResponse.ok) {
          throw new Error("Could not sync session with backend database.");
        }

        const syncData = await syncResponse.json();
        onAuthSuccess(data.session.access_token, syncData.user);
        onClose();
        resetForm();
      }
    } catch (err: any) {
      setErrorMessage(err.message || "An authentication error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setName("");
    setEmail("");
    setPassword("");
    setErrorMessage("");
    setInfoMessage("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div 
        className="w-full max-w-md overflow-hidden rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-2xl transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative p-6 sm:p-8">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-lg cursor-pointer"
            aria-label="Close modal"
          >
            ✕
          </button>

          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-amber-600 flex items-center justify-center text-2xl mx-auto mb-3 shadow-lg shadow-blue-500/10">
              🏛️
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-amber-600 dark:from-blue-400 dark:to-amber-400 bg-clip-text text-transparent">
              {mode === "login" ? "Citizen Login" : "Register Account"}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {mode === "login"
                ? "Enter your credentials to access HYBO Smart City Assistant."
                : "Create an account to save your chat sessions and preferences."}
            </p>
          </div>

          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs font-medium text-red-600 dark:text-red-400">
              ⚠️ {errorMessage}
            </div>
          )}

          {infoMessage && (
            <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-xs font-medium text-green-600 dark:text-green-400">
              ℹ️ {infoMessage}
            </div>
          )}

          <form onSubmit={handleAuth} className="space-y-4">
            {mode === "signup" && (
              <div>
                <label htmlFor="name-input" className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                  Your Full Name
                </label>
                <input
                  id="name-input"
                  type="text"
                  placeholder="e.g. John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  required
                />
              </div>
            )}

            <div>
              <label htmlFor="email-input" className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                Email Address
              </label>
              <input
                id="email-input"
                type="email"
                placeholder="e.g. citizen@hyderabad.gov.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                required
              />
            </div>

            <div>
              <label htmlFor="password-input" className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                Password
              </label>
              <input
                id="password-input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-colors cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/15"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                  Processing...
                </>
              ) : mode === "login" ? (
                "Log In 🔓"
              ) : (
                "Create Account 🚀"
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-xs">
            <span className="text-slate-500">
              {mode === "login" ? "New to HYBO?" : "Already have an account?"}
            </span>{" "}
            <button
              type="button"
              onClick={() => {
                setMode(mode === "login" ? "signup" : "login");
                setErrorMessage("");
                setInfoMessage("");
              }}
              className="font-semibold text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 transition-colors cursor-pointer"
            >
              {mode === "login" ? "Create an account" : "Log in here"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
