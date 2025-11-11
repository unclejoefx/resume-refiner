# Phase 8: Deployment - Detailed Specification

**Timeline**: Week 8+
**Status**: Not Started
**Dependencies**: Phase 7 (Polish and Testing)

## Objectives

Deploy the Resume Refiner application to production, set up CI/CD pipelines, configure monitoring and logging, and ensure the application is secure, scalable, and maintainable in production.

## Tasks Breakdown

### 8.1 Prepare for Production

**Task**: Configure application for production environment

**Steps**:
1. Create production configuration files:
   ```python
   # backend/app/config.py - Update for production
   from pydantic_settings import BaseSettings
   from typing import List
   import os

   class Settings(BaseSettings):
       # Environment
       ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

       # Security
       CLAUDE_API_KEY: str
       SECRET_KEY: str = os.getenv("SECRET_KEY", "")

       # Database
       DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resume_refiner.db")

       # CORS
       ALLOWED_ORIGINS: List[str] = os.getenv(
           "ALLOWED_ORIGINS",
           "http://localhost:5173"
       ).split(",")

       # File upload
       MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))
       UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

       # Rate limiting
       RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

       # Logging
       LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

       class Config:
           env_file = ".env"

       @property
       def is_production(self) -> bool:
           return self.ENVIRONMENT == "production"

   settings = Settings()
   ```

2. Add logging configuration:
   ```python
   # backend/app/logging_config.py
   import logging
   import sys
   from app.config import settings

   def setup_logging():
       logging.basicConfig(
           level=getattr(logging, settings.LOG_LEVEL),
           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
           handlers=[
               logging.StreamHandler(sys.stdout),
               logging.FileHandler('app.log') if settings.is_production else logging.NullHandler()
           ]
       )

   # In main.py
   from app.logging_config import setup_logging

   setup_logging()
   logger = logging.getLogger(__name__)
   ```

3. Create production `.env` template:
   ```bash
   # .env.production
   ENVIRONMENT=production
   CLAUDE_API_KEY=your_production_key
   SECRET_KEY=generate_strong_secret_key
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ALLOWED_ORIGINS=https://yourdomain.com
   MAX_FILE_SIZE=10485760
   UPLOAD_DIR=/var/app/uploads
   RATE_LIMIT_PER_MINUTE=5
   LOG_LEVEL=WARNING
   ```

4. Update frontend for production:
   ```typescript
   // frontend/.env.production
   VITE_API_URL=https://api.yourdomain.com
   ```

**Deliverables**:
- Production configuration
- Logging setup
- Environment-specific settings
- Security configurations

**Acceptance Criteria**:
- Configuration loads from environment variables
- Logging captures important events
- Security settings enforced
- Different configs for dev/prod

---

### 8.2 Choose Deployment Platform

**Task**: Select and prepare deployment platforms

**Recommended Options**:

#### Option A: Render (Easiest - Recommended for MVP)
**Backend:**
- Create `render.yaml`:
  ```yaml
  services:
    - type: web
      name: resume-refiner-api
      env: python
      buildCommand: "cd backend && pip install -r requirements.txt"
      startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
      envVars:
        - key: CLAUDE_API_KEY
          sync: false
        - key: ENVIRONMENT
          value: production
        - key: PYTHON_VERSION
          value: 3.11.0
  ```

**Frontend:**
- Build command: `cd frontend && npm install && npm run build`
- Publish directory: `frontend/dist`

#### Option B: Railway
- Similar to Render, auto-deploys from GitHub
- Good for both frontend and backend
- Supports environment variables

#### Option C: AWS (Most Scalable)
**Backend:**
- AWS Elastic Beanstalk or ECS
- S3 for file storage
- RDS for database

**Frontend:**
- S3 + CloudFront for static hosting
- Route 53 for DNS

#### Option D: Docker + VPS (Most Control)
Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - ENVIRONMENT=production
    volumes:
      - uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  uploads:
```

**Steps for Deployment**:
1. Choose platform based on requirements
2. Set up accounts and credentials
3. Configure deployment scripts
4. Test deployment in staging environment

**Deliverables**:
- Deployment configuration files
- Platform-specific setup
- Documentation for chosen platform

**Acceptance Criteria**:
- Application deploys successfully
- Environment variables configured
- Services accessible via public URLs

---

### 8.3 Set Up CI/CD Pipeline

**Task**: Automate testing and deployment

**Steps**:
1. Create GitHub Actions workflow:
   ```yaml
   # .github/workflows/ci-cd.yml
   name: CI/CD

   on:
     push:
       branches: [main, develop]
     pull_request:
       branches: [main]

   jobs:
     test-backend:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'

         - name: Install dependencies
           run: |
             cd backend
             pip install -r requirements.txt

         - name: Run tests
           run: |
             cd backend
             pytest --cov=app

     test-frontend:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Set up Node.js
           uses: actions/setup-node@v3
           with:
             node-version: '18'

         - name: Install dependencies
           run: |
             cd frontend
             npm install

         - name: Run tests
           run: |
             cd frontend
             npm test

         - name: Build
           run: |
             cd frontend
             npm run build

     deploy:
       needs: [test-backend, test-frontend]
       runs-on: ubuntu-latest
       if: github.ref == 'refs/heads/main'
       steps:
         - uses: actions/checkout@v3

         - name: Deploy to production
           run: |
             echo "Deploy to production"
             # Add deployment commands for chosen platform
   ```

2. Set up GitHub secrets:
   - `CLAUDE_API_KEY`
   - `DATABASE_URL`
   - Platform-specific deployment keys

3. Configure branch protection:
   - Require PR reviews
   - Require status checks to pass
   - Enforce linear history

**Deliverables**:
- CI/CD pipeline configuration
- Automated testing on push
- Automated deployment on merge
- Branch protection rules

**Acceptance Criteria**:
- Tests run automatically on PR
- Deployment triggers on main branch merge
- Failed tests prevent deployment
- Secrets managed securely

---

### 8.4 Configure Domain and SSL

**Task**: Set up custom domain with HTTPS

**Steps**:
1. Purchase domain (optional):
   - Use Namecheap, Google Domains, or Cloudflare

2. Configure DNS:
   - Point domain to deployment platform
   - Add A or CNAME records
   - Example:
     ```
     api.yourdomain.com → backend service
     yourdomain.com → frontend service
     ```

3. Set up SSL certificate:
   - Most platforms provide free SSL (Let's Encrypt)
   - Ensure HTTPS is enforced
   - Configure automatic renewal

4. Update CORS settings:
   ```python
   # backend/app/config.py
   ALLOWED_ORIGINS: List[str] = [
       "https://yourdomain.com",
       "https://www.yourdomain.com"
   ]
   ```

5. Update frontend API URL:
   ```typescript
   // frontend/.env.production
   VITE_API_URL=https://api.yourdomain.com
   ```

**Deliverables**:
- Custom domain configured
- SSL certificate active
- HTTPS enforced
- DNS records set

**Acceptance Criteria**:
- Site accessible via custom domain
- HTTPS works without warnings
- HTTP redirects to HTTPS
- No mixed content warnings

---

### 8.5 Set Up Monitoring and Logging

**Task**: Implement monitoring and error tracking

**Steps**:
1. Set up error tracking (choose one):

   **Option A: Sentry**
   ```bash
   # Backend
   pip install sentry-sdk[fastapi]
   ```

   ```python
   # backend/app/main.py
   import sentry_sdk

   if settings.is_production:
       sentry_sdk.init(
           dsn=settings.SENTRY_DSN,
           traces_sample_rate=0.1,
       )
   ```

   **Option B: LogRocket (Frontend)**
   ```bash
   npm install logrocket
   ```

   ```typescript
   // frontend/src/main.tsx
   import LogRocket from 'logrocket';

   if (import.meta.env.PROD) {
     LogRocket.init('your-app-id');
   }
   ```

2. Set up application monitoring:
   - Use platform-native monitoring (Render, Railway)
   - Or external: New Relic, Datadog

3. Configure logging:
   ```python
   # Log important events
   logger.info(f"Resume uploaded: {upload_id}")
   logger.warning(f"Analysis failed: {error}")
   logger.error(f"Critical error: {exception}")
   ```

4. Set up health checks:
   ```python
   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.now().isoformat(),
           "version": "1.0.0"
       }
   ```

5. Configure alerting:
   - Set up alerts for errors
   - Monitor API response times
   - Track upload failures
   - Monitor disk space (for file uploads)

**Deliverables**:
- Error tracking configured
- Application monitoring active
- Logging to centralized system
- Alerts configured

**Acceptance Criteria**:
- Errors captured and reported
- Can view application metrics
- Alerts sent for critical issues
- Logs searchable and retained

---

### 8.6 Performance and Security

**Task**: Optimize and secure production deployment

**Steps**:
1. Enable caching:
   ```python
   # Add caching headers
   @app.get("/api/something")
   async def something(response: Response):
       response.headers["Cache-Control"] = "public, max-age=3600"
       return data
   ```

2. Configure CDN (optional):
   - Use Cloudflare for static assets
   - Cache frontend build files

3. Database optimization:
   - Add indexes for common queries
   - Set up connection pooling
   - Configure backups

4. File storage:
   - Consider S3 for file uploads (instead of local storage)
   - Implement automatic cleanup of old files

5. Security headers:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   from fastapi.middleware.trustedhost import TrustedHostMiddleware

   app.add_middleware(
       TrustedHostMiddleware,
       allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
   )

   @app.middleware("http")
   async def add_security_headers(request: Request, call_next):
       response = await call_next(request)
       response.headers["X-Content-Type-Options"] = "nosniff"
       response.headers["X-Frame-Options"] = "DENY"
       response.headers["X-XSS-Protection"] = "1; mode=block"
       return response
   ```

6. Rate limiting (already configured in Phase 7)

7. Environment secrets:
   - Never commit secrets to git
   - Use platform's secret management
   - Rotate keys periodically

**Deliverables**:
- Caching configured
- Security headers added
- Database optimized
- File storage strategy
- Secrets secured

**Acceptance Criteria**:
- Response times optimized
- Security scan passes
- No secrets in git
- Rate limiting works

---

### 8.7 Documentation and Handoff

**Task**: Prepare final documentation

**Steps**:
1. Create deployment documentation:
   ```markdown
   # Deployment Guide

   ## Prerequisites
   - Render/Railway account
   - Domain name (optional)
   - Claude API key

   ## Deployment Steps
   1. Fork repository
   2. Connect to Render/Railway
   3. Set environment variables
   4. Deploy

   ## Environment Variables
   - CLAUDE_API_KEY: Your Claude API key
   - DATABASE_URL: PostgreSQL connection string
   - ALLOWED_ORIGINS: Frontend domain

   ## Monitoring
   - Dashboard: [URL]
   - Logs: [URL]
   - Errors: [URL]

   ## Troubleshooting
   - Issue: Upload fails
     Solution: Check file size limits

   - Issue: AI analysis not working
     Solution: Verify Claude API key
   ```

2. Create operations runbook:
   ```markdown
   # Operations Runbook

   ## Common Tasks

   ### Deploy new version
   1. Merge PR to main
   2. CI/CD auto-deploys
   3. Verify health check

   ### Roll back deployment
   1. Go to platform dashboard
   2. Select previous deployment
   3. Click "Redeploy"

   ### View logs
   1. Access platform dashboard
   2. Navigate to logs section
   3. Filter by service/time

   ### Update environment variable
   1. Go to platform settings
   2. Update variable
   3. Restart service

   ## Monitoring

   ### Key Metrics
   - API response time: <2s
   - Error rate: <1%
   - Uptime: >99%

   ### Alerts
   - High error rate
   - Slow response times
   - Service down
   ```

3. Create changelog:
   ```markdown
   # Changelog

   ## Version 1.0.0 (2025-XX-XX)

   ### Features
   - Document upload (PDF, DOCX)
   - AI-powered content analysis
   - Grammar checking
   - ATS optimization
   - Format standardization
   - Export to PDF/DOCX

   ### Security
   - File type validation
   - Size limits
   - Rate limiting
   - HTTPS enforced
   ```

**Deliverables**:
- Deployment guide
- Operations runbook
- Changelog
- Architecture diagram

**Acceptance Criteria**:
- Documentation complete and accurate
- New developer can deploy from docs
- Operations tasks documented
- Version history tracked

---

### 8.8 Launch Checklist

**Task**: Final pre-launch verification

**Pre-Launch Checklist**:
- [ ] All tests passing
- [ ] Production environment configured
- [ ] SSL certificate active
- [ ] Domain pointing to services
- [ ] Environment variables set
- [ ] Error tracking configured
- [ ] Monitoring active
- [ ] Backups configured
- [ ] Rate limiting tested
- [ ] CORS configured correctly
- [ ] File uploads work
- [ ] Analysis features work
- [ ] Export features work
- [ ] Mobile responsive
- [ ] Accessibility tested
- [ ] Performance benchmarked
- [ ] Security scan completed
- [ ] Documentation complete
- [ ] Support plan in place

**Post-Launch Tasks**:
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Gather user feedback
- [ ] Plan improvements
- [ ] Schedule maintenance

**Deliverables**:
- Completed launch checklist
- Production application live
- Monitoring dashboard active

**Acceptance Criteria**:
- Application accessible to users
- All features working
- No critical issues
- Monitoring shows healthy status

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│                    Users                         │
└────────────────┬────────────────────────────────┘
                 │
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────┐
│              CDN / Load Balancer                 │
└────────────┬─────────────────────┬───────────────┘
             │                     │
             │ Frontend            │ Backend
             ▼                     ▼
┌────────────────────┐   ┌──────────────────────┐
│   React Frontend   │   │   FastAPI Backend    │
│   (Static Files)   │   │   (Python)           │
└────────────────────┘   └──────────┬───────────┘
                                    │
                         ┌──────────┼──────────┐
                         │          │          │
                         ▼          ▼          ▼
                   ┌──────────┐ ┌─────┐ ┌──────────┐
                   │ Database │ │ S3  │ │ Claude   │
                   │(Postgres)│ │Files│ │   API    │
                   └──────────┘ └─────┘ └──────────┘
```

## Cost Estimates

### Monthly Costs (Approximate)

**Option A: Render (MVP)**
- Backend: $7-25/month
- Frontend: $0 (static site)
- Database: $7/month (PostgreSQL)
- Total: ~$15-35/month

**Option B: Railway**
- Similar to Render: $15-40/month

**Option C: AWS**
- EC2/ECS: $20-50/month
- S3: $1-5/month
- RDS: $15-30/month
- CloudFront: $1-10/month
- Total: ~$40-100/month

**Additional Costs:**
- Domain: $10-15/year
- Claude API: Pay per use (~$0.05-0.20 per resume)
- Monitoring: $0-50/month (depending on service)

## Testing Checklist

### Pre-Deployment
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Backup and restore tested

### Post-Deployment
- [ ] Health check responds
- [ ] Can upload files
- [ ] Can parse files
- [ ] Can run analysis
- [ ] Can export files
- [ ] Error tracking works
- [ ] Logs are captured
- [ ] Alerts fire correctly

## Dependencies

- Phase 7 (Polish and Testing) completed
- All features tested and working
- Documentation complete

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Deployment fails | Test in staging; have rollback plan |
| High traffic crashes server | Implement caching and rate limiting |
| Claude API costs too high | Monitor usage; implement caching |
| Data loss | Regular backups; use managed database |
| Security breach | Follow security best practices; regular audits |

## Success Metrics

- Deployment completes successfully
- Application accessible 24/7
- Response times meet targets (<2s)
- Error rate <1%
- Uptime >99%
- User satisfaction high
- No security incidents

## Next Steps

After deployment:
1. Monitor metrics and logs daily
2. Gather user feedback
3. Plan feature improvements
4. Optimize based on usage patterns
5. Scale as needed
6. Regular security updates
