"use client";

import React, { useState } from "react";

interface UserProfile {
  id: string;
  phone_number: string;
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
  const [name, setName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [devOtpCode, setDevOtpCode] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneNumber.trim()) return;

    setIsLoading(true);
    setErrorMessage("");
    setDevOtpCode(null);

    try {
      const response = await fetch("http://localhost:8000/api/auth/send-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          phone_number: phoneNumber,
          name: name.trim() || undefined,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to send OTP code.");
      }

      setStep("otp");
      if (data.dev_mode && data.dev_otp) {
        setDevOtpCode(data.dev_otp);
        // Auto-fill dev otp for easy testing
        setOtp(data.dev_otp);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp.trim()) return;

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/auth/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          phone_number: phoneNumber,
          otp: otp,
          name: name.trim() || undefined,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "OTP verification failed.");
      }

      onAuthSuccess(data.access_token, data.user);
      onClose();
      // Reset form
      setName("");
      setPhoneNumber("");
      setOtp("");
      setStep("phone");
      setDevOtpCode(null);
    } catch (err: any) {
      setErrorMessage(err.message || "Invalid OTP. Please try again.");
    } finally {
      setIsLoading(false);
    }
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
              {step === "phone" ? "Citizen Login" : "Verify OTP"}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {step === "phone"
                ? "Enter your name and phone number to access HYBO Smart City Assistant."
                : `We've sent a code to your phone number.`}
            </p>
          </div>

          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs font-medium text-red-600 dark:text-red-400">
              ⚠️ {errorMessage}
            </div>
          )}

          {step === "phone" ? (
            <form onSubmit={handleSendOtp} className="space-y-4">
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

              <div>
                <label htmlFor="phone-input" className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                  Mobile Phone Number
                </label>
                <input
                  id="phone-input"
                  type="tel"
                  placeholder="e.g. +91 98765 43210"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
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
                    Sending Code...
                  </>
                ) : (
                  "Request Verification Code 🚀"
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div>
                <label htmlFor="otp-input" className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                  Enter 6-Digit OTP Code
                </label>
                <input
                  id="otp-input"
                  type="text"
                  maxLength={6}
                  placeholder="123456"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="w-full text-center bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-lg font-bold tracking-[0.5em] text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  required
                />
              </div>

              {devOtpCode && (
                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-center">
                  <p className="text-[10px] text-amber-600 dark:text-amber-400 font-semibold mb-1">
                    🛠️ DEV FALLBACK MODE
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-300">
                    Use simulated verification code: <strong className="text-sm font-bold text-amber-500 dark:text-amber-400 tracking-wider ml-1">{devOtpCode}</strong>
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-colors cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/15"
              >
                {isLoading ? (
                  <>
                    <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                    Verifying Code...
                  </>
                ) : (
                  "Confirm & Log In 🔓"
                )}
              </button>

              <button
                type="button"
                onClick={() => setStep("phone")}
                disabled={isLoading}
                className="w-full text-center text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 cursor-pointer py-1 font-medium transition-colors"
              >
                ← Back to Phone input
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
