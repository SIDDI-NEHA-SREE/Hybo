"use client";

import React, { useState, useRef } from "react";

interface ChatInputProps {
  onSend: (text: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim() || isLoading || isTranscribing) return;
    onSend(inputValue);
    setInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: "file" | "image") => {
    const files = e.target.files;
    if (files && files.length > 0) {
      alert(`Selected ${type}: ${files[0].name}. (File & Image processing will be integrated in subsequent phases).`);
    }
  };

  // Start Voice Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setIsTranscribing(true); // show loading state during transcription
        
        try {
          const formData = new FormData();
          formData.append("file", audioBlob, "recording.wav");

          const response = await fetch("http://localhost:8000/api/voice/transcribe", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) throw new Error("Transcription request failed");

          const data = await response.json();
          if (data.transcription) {
            onSend(data.transcription);
          }
        } catch (err) {
          console.error("Transcription error:", err);
          alert("Transcription failed. (FastAPI backend is offline or AWS Transcribe is unconfigured).");
        } finally {
          setIsTranscribing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Failed to access microphone:", err);
      alert("Microphone permission denied or unsupported by browser.");
    }
  };

  // Stop Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop all tracks on the stream to release the mic
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const isInputDisabled = isLoading || isRecording || isTranscribing;

  return (
    <div className="p-4 sm:p-6 bg-white dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 transition-colors">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-full pl-5 pr-2.5 py-1.5 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/15 transition-all">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isInputDisabled}
            placeholder={
              isRecording 
                ? "Recording voice... Click mic to stop" 
                : isTranscribing
                  ? "Transcribing voice input..."
                  : isLoading 
                    ? "Generating response..." 
                    : "Ask about Hyderabad or Telangana..."
            }
            className="flex-1 bg-transparent border-none outline-none text-sm text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500"
            aria-label="Chat input"
          />

          {/* Hidden inputs */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => handleFileUpload(e, "file")}
            className="hidden"
            accept=".pdf,.docx,.txt"
            aria-label="Upload document"
          />
          <input
            type="file"
            ref={imageInputRef}
            onChange={(e) => handleFileUpload(e, "image")}
            className="hidden"
            accept="image/*"
            aria-label="Upload image"
          />

          {/* Action Buttons */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isInputDisabled}
            className="p-1.5 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 cursor-pointer disabled:opacity-50 transition-colors"
            title="Upload Document (.pdf, .docx, .txt)"
          >
            📎
          </button>
          <button
            type="button"
            onClick={() => imageInputRef.current?.click()}
            disabled={isInputDisabled}
            className="p-1.5 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 cursor-pointer disabled:opacity-50 transition-colors"
            title="Upload Image"
          >
            📷
          </button>
          
          {/* Microphone control button */}
          <button
            type="button"
            disabled={isLoading || isTranscribing}
            onClick={toggleRecording}
            className={`p-1.5 rounded-full cursor-pointer disabled:opacity-50 transition-all ${
              isRecording 
                ? "bg-red-500/20 text-red-500 hover:bg-red-500/30 scale-110 animate-pulse" 
                : "hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
            }`}
            title={isRecording ? "Stop Recording" : "Voice Assistance"}
          >
            🎙️
          </button>

          <button
            type="submit"
            disabled={!inputValue.trim() || isInputDisabled}
            className="ml-1 p-2 rounded-full bg-blue-600 hover:bg-blue-500 text-white disabled:bg-slate-300 dark:disabled:bg-slate-800 disabled:text-slate-500 cursor-pointer disabled:cursor-default transition-colors shadow-sm"
            title="Send message"
          >
            🚀
          </button>
        </div>
      </form>
    </div>
  );
}
