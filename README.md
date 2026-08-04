<<<<<<< HEAD
# HYBO – City InsideOut

HYBO is an AI-powered Smart City Digital Twin platform for Hyderabad and Telangana. Developed by a team of three university students, the platform aims to democratize access to public services, local administration, tourism, transit, and emergency care.

---

## 1. Project Overview & Screenshots

HYBO Assistant features a professional, responsive, accessibility-friendly dashboard supporting light and dark modes, inline multilingual selections, voice transcriptions, and document upload actions.

### Project Screenshots Placeholder
```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                [SCREENSHOT: HYBO Assistant Dashboard]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack Overview

### Frontend
- **Framework**: Next.js 15 (React 19, App Router)
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI (ASGI / Uvicorn)
- **Language**: Python 3.14
- **Environment**: Pydantic Settings

---

## 3. Project Directory Structure

```text
HYBO2/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py           # Application entrypoint
│   │   ├── config.py         # Config loader
│   │   ├── routers/          # Route controllers (chat, voice, files)
│   │   ├── services/         # Orchestrators (AI, Scraper, Voice)
│   │   └── utils/            # Logs & converters
│   ├── Dockerfile            # Backend Docker spec
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Next.js Frontend
│   ├── src/
│   │   ├── components/       # Reusable components (Header, Sidebar, ChatInput)
│   │   └── app/
│   │       ├── layout.tsx    # Root layout
│   │       └── page.tsx      # Core orchestrator and streaming simulator
│   ├── Dockerfile            # Frontend Docker spec
│   ├── package.json          # Node dependencies
│   └── tsconfig.json         # TypeScript configuration
│
├── docker-compose.yml        # Local Multi-Container setup
├── DEPLOYMENT.md             # Production Deployment Specification
├── PROJECT_LOG.md            # Action decision log
└── CHANGELOG.md              # Releases registry
```

---

## 4. REST API Reference

### 1. POST `/api/chat`
Processes conversational queries.
- **Request Body**:
  ```json
  {
    "message": "Where is the nearest hospital in Hyderabad?",
    "language": "en",
    "session_id": "session-123"
  }
  ```

### 2. POST `/api/voice/transcribe`
Transcribes binary audio uploads.
- **Request**: `multipart/form-data` containing `file` key.

### 3. POST `/api/voice/synthesize`
Synthesizes text into speech.
- **Request**: Form parameters `text` (string) and `language` (string).
- **Response**: `audio/mpeg` audio stream.

### 4. POST `/api/files/analyze`
Extracts and analyzes PDF, DOCX, TXT, or Image files.
- **Request**: Form parameters `file` (binary), `action` (summarize/translate/explain/extract), and `language`.

---

## 5. Deployment Guide
For complete Vercel and AWS App Runner deploy steps, check out:
- **[DEPLOYMENT.md](file:///d:/4yr/MP/HYBO2/DEPLOYMENT.md)**

---

## 6. Future Project Roadmap

### Phase 1: AI Chatbot Assistant (Current)
- Bounded Hyderabad/Telangana rules.
- Multilingual and voice parsing.
- Transient document OCR analysis.

### Phase 2: RAG & Multi-Agent System
- Connect local vector database (ChromaDB/PGVector) for cached government documents.
- Deploy specialized sub-agents representing GHMC, TSRTC, and Revenue portals.

### Phase 3: Digital Twin Integration
- Render 3D map of Hyderabad using MapLibre GL / Cesium.js.
- Feed live WebSockets streams carrying IoT telemetry (transit location, air index, water levels).
=======

>>>>>>> 66ef7fa5b9640182af383498f40fd9008e70b6ce
