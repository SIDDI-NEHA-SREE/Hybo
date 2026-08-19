# HYBO – Deployment Specification Guide

This document details the configuration requirements, environment specifications, and step-by-step procedures to deploy **HYBO – City InsideOut** to production platforms.

---

## 1. Production Tech Stack & Targets

- **Frontend client**: Next.js (TypeScript) deployed to **Vercel** (Global CDN edge delivery).
- **Backend API**: FastAPI (Python 3.11) containerized and deployed to **Render** (via Web Service with Docker).
- **Database / Auth**: **Supabase** (PostgreSQL database & Supabase Auth).
- **AI & Processing Services**: Amazon Bedrock, Amazon Textract, Amazon Transcribe, Amazon Polly.

---

## 2. Frontend Deployment (Vercel)

Vercel is the recommended hosting platform for the Next.js app router.

### Step-by-Step Instructions

1. **Connect Repository**:
   - Go to the Vercel Dashboard and click **Add New Project**.
   - Import the `HYBO2` monorepo.
2. **Configure Build Settings**:
   - Set **Root Directory** to `frontend`.
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`
3. **Environment Variables**:
   Configure the following environment variables in the project settings:
   - `NEXT_PUBLIC_API_URL`: The production HTTP URL of your FastAPI backend hosted on Render (e.g., `https://hybo-backend.onrender.com`).
   - `NEXT_PUBLIC_SUPABASE_URL`: The URL of your Supabase project (from Settings > API).
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: The public/anon key of your Supabase project.
4. **Deploy**:
   - Click **Deploy**. Vercel will automatically build the static assets.

---

## 3. Backend Deployment (Render)

Render is the recommended hosting platform for the backend container.

### Step-by-Step Instructions

1. **Create Web Service on Render**:
   - Go to the Render Dashboard, click **New +**, and select **Web Service**.
   - Connect your GitHub repository.
2. **Configure Settings**:
   - **Name**: `hybo-backend`
   - **Region**: Select your preferred region.
   - **Branch**: `main`
   - **Root Directory**: `backend` (or leave empty if building the root workspace, but `backend` contains the Dockerfile).
   - **Runtime**: `Docker`
3. **Configure Environment Variables**:
   Configure the following variables in the Render environment settings:
   - `PORT`: (Auto-provided by Render, but default is `8000`)
   - `SUPABASE_URL`: Your Supabase Project URL.
   - `SUPABASE_ANON_KEY`: Your Supabase Anon Key.
   - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase Service Role Key (used securely on backend only).
   - `FRONTEND_URL`: Your production Vercel frontend URL (e.g. `https://hybo-frontend.vercel.app`).
   - Add any other AWS credentials needed for Bedrock, Polly, etc. (e.g. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`).
4. **Deploy**:
   - Click **Create Web Service**. Render will build and deploy the container based on the `backend/Dockerfile` automatically.

---

## 4. Supabase Setup

To initialize your database, create a `profiles` table in the Supabase SQL editor:

```sql
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  name text,
  email text,
  phone_number text,
  role text default 'citizen',
  created_at timestamptz default timezone('utc'::text, now()) not null,
  updated_at timestamptz default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table public.profiles enable row level security;

-- Create policy to allow users to select/update their own profile
create policy "Allow users to view own profile" on public.profiles
  for select using (auth.uid() = id);

create policy "Allow users to update own profile" on public.profiles
  for update using (auth.uid() = id);

create policy "Allow service role full access" on public.profiles
  for all using (true);
```

---

## 5. Production Environment Variables Checklist

### Frontend (`frontend/.env.production`)
| Variable Name | Description | Value Example |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Endpoint of the live FastAPI server on Render | `https://hybo-backend.onrender.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project API URL | `https://xyz.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public client key for auth | `eyJhbGci...` |

### Backend (`backend/.env.production`)
| Variable Name | Description | Value Example |
| :--- | :--- | :--- |
| `APP_NAME` | Identifier for the FastAPI application | `HYBO-Assistant-Prod` |
| `DEBUG` | Disables debug logs and Swagger in prod | `False` |
| `PORT` | Container binding port | `8000` |
| `HOST` | Container binding host | `0.0.0.0` |
| `SUPABASE_URL` | Supabase API connection URL | `https://xyz.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase public anon key | `eyJhbGci...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase admin secret key | `eyJhbGci...` |
| `FRONTEND_URL` | Production allowed CORS origin | `https://hybo-frontend.vercel.app` |
