# Hybo
City Inside Out - MAjor Project
https://tgdex.telangana.gov.in
https://data.telangana.gov.in
Replit link-  https://hybo-city-builder--panduneedmail.replit.app/dashboard
Frontend: Vercel
Backend: Railway
Database: Neon PostgreSQL
Source Control: GitHub
Tech stack
| Component      | Recommendation                                              | Why                                                            |
| -------------- | ----------------------------------------------------------- | -------------------------------------------------------------- |
| Frontend       | **Next.js (React) on Vercel**                               | Fast, SEO-friendly, global CDN, excellent developer experience |
| Backend        | **FastAPI or Express/NestJS on AWS ECS (or EC2 initially)** | Easy to scale, production-ready                                |
| Database       | **Amazon RDS PostgreSQL**                                   | Managed, reliable, backups, high availability                  |
| File Storage   | **Amazon S3**                                               | Images, documents, PDFs, datasets                              |
| Cache          | **Amazon ElastiCache (Redis)**                              | Faster responses and session caching                           |
| Authentication | **Clerk** or **Auth0**, or your own JWT system initially    | Secure login and OAuth support                                 |
| AI             | Gemini/OpenAI APIs (or a self-hosted model later)           | AI assistant capabilities                                      |
| Maps           | Google Maps Platform or Mapbox                              | Navigation and location services                               |
| Monitoring     | Amazon CloudWatch + Sentry                                  | Logs, metrics, error tracking                                  |
| CDN            | CloudFront (or Vercel's CDN)                                | Fast content delivery                                          |
| Domain         | Route 53                                                    | DNS management  


                                               |

Architecture:

                    Users
                      │
               hybo.city
                      │
            Vercel (Next.js Frontend)
                      │
                 HTTPS API Calls
                      │
          AWS Application Load Balancer
                      │
        ECS / EC2 (Express or FastAPI)
          │        │           │
          │        │           │
      Amazon RDS  Amazon S3  Redis
     PostgreSQL   File Store Cache
          │
      AI APIs (Gemini/OpenAI)
          │
 Government APIs & Open Data