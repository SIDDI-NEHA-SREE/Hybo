# Project Log - HYBO: City InsideOut

This file tracks the timeline, architectural milestones, and key engineering decisions for the HYBO Major Project.

## Project Metadata
- **Project Name**: HYBO – City InsideOut
- **Objective**: AI-Powered Smart City Digital Twin platform for Hyderabad and Telangana
- **Team**: 3 University Students (Major Project)

---

## Log of Key Architectural Decisions (ADR)

### ADR 001: Separation of Client and Server Layers
- **Status**: APPROVED
- **Context**: Decouple frontend from backend via RESTful APIs and WebSockets.

### ADR 002: Transient Government Data Policy
- **Status**: APPROVED
- **Context**: Government rules change dynamically. Scrape live data rather than saving permanently.

### ADR 003: Transition to Next.js, TypeScript, and Tailwind CSS
- **Status**: APPROVED
- **Context**: Migrated to Next.js skeleton with TS and Tailwind.

### ADR 004: Unicode Script Mapping for Localized Language Detection
- **Status**: APPROVED
- **Context**: Real-time language detection must be lightweight and local.

### ADR 005: AWS Bedrock Claude 3.5 Integration with Offline Mock Fallback
- **Status**: APPROVED
- **Context**: Offline fallback simulator framework.

### ADR 006: Integration of AWS Transcribe and AWS Polly with Dummy MP3 Generator
- **Status**: APPROVED
- **Context**: Voice queries require STT and TTS services.

### ADR 007: Transient In-Memory Document Parsing and Amazon Textract OCR Integration
- **Status**: APPROVED
- **Context**: In-memory stream parser.

### ADR 008: Serverless Production Deployment Architecture on AWS & Vercel
- **Status**: APPROVED
- **Context**: Decoupled monorepos need independent cloud hosts.
- **Decision**: Deploy Next.js to **Vercel** for fast Edge loading. Deploy FastAPI backend inside Docker containers on **AWS App Runner** to handle automatic HTTPS, load-balancing, and autoscaling.
- **Consequences**: High availability, automatic SSL, zero-downtime deployments, and minimizes server management overhead.
