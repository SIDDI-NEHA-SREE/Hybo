"use client";

import React, { useState } from "react";

interface UserProfile {
  id: string;
  phone_number: string;
  name: string;
  role: string;
  created_at: string;
}

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserProfile | null;
  token: string | null;
  onUpdateUser: (updatedUser: UserProfile) => void;
  onLogout: () => void;
}

export default function ProfileModal({
  isOpen,
  onClose,
  user,
  token,
  onUpdateUser,
  onLogout,
}: ProfileModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(user?.name || "");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  if (!isOpen || !user) return null;

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editedName.trim() || !token) return;

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(`http://localhost:8000/api/auth/profile?name=${encodeURIComponent(editedName.trim())}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to update profile name.");
      }

      onUpdateUser(data);
      setIsEditing(false);
    } catch (err: any) {
      setErrorMessage(err.message || "An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartEdit = () => {
    setEditedName(user.name);
    setIsEditing(true);
    setErrorMessage("");
  };

  const formatDate = (isoStr: string) => {
    try {
      return new Date(isoStr).toLocaleDateString([], {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch (e) {
      return isoStr;
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
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-blue-600 to-amber-600 flex items-center justify-center text-3xl mx-auto mb-3 shadow-lg shadow-blue-500/10 text-white font-bold">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">
              Citizen Profile
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Manage your personal settings
            </p>
          </div>

          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs font-medium text-red-600 dark:text-red-400">
              ⚠️ {errorMessage}
            </div>
          )}

          <div className="space-y-4">
            {isEditing ? (
              <form onSubmit={handleUpdateProfile} className="space-y-3">
                <div>
                  <label htmlFor="edit-name" className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                    Update Name
                  </label>
                  <input
                    id="edit-name"
                    type="text"
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    required
                    autoFocus
                  />
                </div>
                <div className="flex gap-2.5 pt-1">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition-colors cursor-pointer disabled:opacity-50"
                  >
                    {isLoading ? "Saving..." : "Save Changes"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    disabled={isLoading}
                    className="flex-1 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-medium text-xs transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/80 rounded-xl p-4 space-y-3.5 text-sm">
                <div className="flex justify-between items-center pb-2.5 border-b border-slate-200/50 dark:border-slate-800/50">
                  <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Name:</span>
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{user.name}</span>
                    <button
                      onClick={handleStartEdit}
                      className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-800 text-xs text-blue-500 cursor-pointer"
                      title="Edit Name"
                    >
                      ✏️
                    </button>
                  </div>
                </div>
                <div className="flex justify-between items-center pb-2.5 border-b border-slate-200/50 dark:border-slate-800/50">
                  <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Mobile Phone:</span>
                  <span className="font-mono text-xs text-slate-800 dark:text-slate-200">{user.phone_number}</span>
                </div>
                <div className="flex justify-between items-center pb-2.5 border-b border-slate-200/50 dark:border-slate-800/50">
                  <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Role:</span>
                  <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                    {user.role}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 dark:text-slate-400 text-xs font-medium">Joined:</span>
                  <span className="text-xs text-slate-600 dark:text-slate-400">{formatDate(user.created_at)}</span>
                </div>
              </div>
            )}

            <div className="border-t border-slate-200 dark:border-slate-800 pt-5 flex flex-col gap-2">
              <button
                onClick={() => {
                  onLogout();
                  onClose();
                }}
                className="w-full py-2.5 rounded-xl border border-red-500/20 text-red-500 bg-red-500/5 hover:bg-red-500/10 text-xs font-semibold tracking-wide transition-all cursor-pointer text-center"
              >
                Log Out Session 📴
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
