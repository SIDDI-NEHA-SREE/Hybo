# HYBO – Deployment Specification Guide

This document details the configuration requirements, environment specifications, and step-by-step procedures to deploy **HYBO – City InsideOut** to production platforms.

---

## 1. Production Tech Stack & Targets

- **Frontend client**: Next.js (TypeScript) deployed to **Vercel** (Global CDN edge delivery).
- **Backend API**: FastAPI (Python 3.14) containerized and deployed to **AWS App Runner** or **AWS Lambda**.
- **Orchestration**: Docker & AWS Elastic Container Registry (ECR).
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
   - `NEXT_PUBLIC_API_URL`: The production HTTP URL of your FastAPI backend hosted on AWS (e.g., `https://api.hybo.in`).
4. **Deploy**:
   - Click **Deploy**. Vercel will automatically build the static assets and spin up the edge route configurations.

---

## 3. Backend Deployment (AWS App Runner)

AWS App Runner is the easiest, most cost-effective way to deploy containerized FastAPI backends with automatic scaling, SSL, and load balancing.

### Step-by-Step Instructions

1. **Create AWS ECR Repository**:
   Create a private repository to hold your backend Docker images:
   ```bash
   aws ecr create-repository --repository-name hybo-backend --region us-east-1
   ```
2. **Build and Push Docker Image**:
   ```bash
   # Log in to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build image (make sure you are in backend/ directory)
   cd backend
   docker build -t hybo-backend .

   # Tag image
   docker tag hybo-backend:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/hybo-backend:latest

   # Push to cloud
   docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/hybo-backend:latest
   ```
3. **Create App Runner Service**:
   - Go to the **AWS App Runner Console** and click **Create Service**.
   - Source: **Container Registry** -> **Amazon ECR**.
   - Image URI: Select `<aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/hybo-backend:latest`.
   - Deployment Trigger: Set to **Automatic** (re-deploys when you push a new image).
4. **Configure Container Settings**:
   - Port: `8000`
   - Environment Variables: Configure production credentials (see checklist below).
5. **IAM Role Permission**:
   - Under **Security**, attach an IAM Instance Role that contains the following permissions:
     - `bedrock:InvokeModel`
     - `textract:DetectDocumentText`
     - `polly:SynthesizeSpeech`
     - `transcribe:StartTranscriptionJob`
6. **Deploy**:
   - Click **Create & Deploy**. AWS will spin up the load-balanced, SSL-certified Fargate instances.

---

## 4. Production Environment Variables Checklist

### Frontend (`frontend/.env.production`)
| Variable Name | Description | Value Example |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Endpoint of the live FastAPI server | `https://api.hybo.in` |

### Backend (`backend/.env.production`)
| Variable Name | Description | Value Example |
| :--- | :--- | :--- |
| `APP_NAME` | Identifier for the FastAPI application | `HYBO-Assistant-Prod` |
| `DEBUG` | Disables debug logs and Swagger in prod | `False` |
| `PORT` | Container binding port | `8000` |
| `HOST` | Container binding host | `0.0.0.0` |
| `AWS_REGION` | AWS regional deployment | `us-east-1` |
| `BEDROCK_MODEL_ID` | Production Claude model ID | `anthropic.claude-3-5-sonnet-20240620-v1:0` |

---

## 5. Pre-Deployment Testing Checklist

Run these sanity checks prior to pointing domains to the production build:

- [ ] **FastAPI Swagger Access**: Verify `/docs` works in dev and is disabled in prod by setting `DEBUG=False`.
- [ ] **Telangana Scope Filter**: Submit a query about "New York City". Confirm that the system prompt rejects the query politely.
- [ ] **Multilingual Integrity**: Submit a query in Telugu script (హైదరాబాద్) and verify the assistant responds in Telugu.
- [ ] **Transient Document Upload Check**: Upload a PDF and call the `extract` action. Verify that no file is written to `/tmp` or the filesystem.
- [ ] **Image OCR (AWS Textract)**: Upload a PNG and verify that Textract returns extracted text lines.
- [ ] **Voice Playback Stream**: Submit a TTS request and verify the response headers contain `Content-Type: audio/mpeg` and play audio cleanly.
