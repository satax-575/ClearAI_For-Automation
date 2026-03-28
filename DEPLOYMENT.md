# 🚀 ClearPath Deployment Guide

Complete guide for deploying ClearPath to Firebase and Google Cloud Platform.

---

## 📋 Prerequisites

### Required Accounts
1. **Firebase Account** (free tier available)
   - Go to https://console.firebase.google.com
   - Create new project: "clearpath-customs"

2. **Google Cloud Account** (free $300 credit)
   - Enable billing
   - Enable APIs: Cloud Run, Cloud Build, Firestore, Storage

3. **API Keys**
   - OpenAI API key (https://platform.openai.com/api-keys)
   - Anthropic API key (https://console.anthropic.com)

### Required Tools
```bash
# Node.js 18+
node --version

# Python 3.11+
python --version

# Firebase CLI
npm install -g firebase-tools

# Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install
gcloud --version

# Docker (optional, for local testing)
docker --version
```

---

## 🔧 Step 1: Firebase Setup

### 1.1 Initialize Firebase Project

```bash
# Login to Firebase
firebase login

# Initialize project
cd clearpath-customs
firebase init

# Select:
# - Firestore
# - Storage
# - Hosting
# - (Optional) Functions

# Choose existing project or create new: clearpath-customs
```

### 1.2 Configure Firestore

```bash
# Deploy Firestore rules and indexes
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes
```

### 1.3 Configure Storage

```bash
# Deploy Storage rules
firebase deploy --only storage
```

### 1.4 Get Firebase Config

1. Go to Firebase Console → Project Settings
2. Scroll to "Your apps" → Web app
3. Copy configuration object
4. Save to `frontend/.env.local`:

```env
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=clearpath-customs.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=clearpath-customs
VITE_FIREBASE_STORAGE_BUCKET=clearpath-customs.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abc123
```

### 1.5 Download Service Account Key

1. Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save as `backend/firebase-credentials.json`
4. **NEVER commit this file to git!**

---

## 🌐 Step 2: Deploy Frontend to Firebase Hosting

### 2.1 Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local with Firebase config (see above)
cp .env.example .env.local
# Edit .env.local with your values

# Build for production
npm run build
```

### 2.2 Deploy to Firebase

```bash
# From project root
firebase deploy --only hosting

# Your app will be live at:
# https://clearpath-customs.web.app
# https://clearpath-customs.firebaseapp.com
```

### 2.3 Configure Custom Domain (Optional)

```bash
# Add custom domain
firebase hosting:channel:deploy production --only hosting

# Follow instructions to add DNS records
# Example: clearpath.ai → Firebase Hosting
```

---

## ☁️ Step 3: Deploy Backend to Google Cloud Run

### 3.1 Setup Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project clearpath-customs

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3.2 Store Secrets

```bash
# Store API keys as secrets
echo -n "sk-your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "sk-ant-your-anthropic-key" | gcloud secrets create anthropic-api-key --data-file=-

# Store Firebase credentials
gcloud secrets create firebase-credentials --data-file=backend/firebase-credentials.json
```

### 3.3 Deploy Backend

```bash
cd backend

# Deploy to Cloud Run
gcloud run deploy clearpath-api \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,USE_CLAUDE=true" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest,FIREBASE_CREDENTIALS_PATH=firebase-credentials:latest"

# Note the service URL (e.g., https://clearpath-api-xxx-uc.a.run.app)
```

### 3.4 Update Frontend with Backend URL

```bash
# Update frontend/.env.local
VITE_API_URL=https://clearpath-api-xxx-uc.a.run.app

# Rebuild and redeploy frontend
cd ../frontend
npm run build
cd ..
firebase deploy --only hosting
```

---

## 🐳 Step 4: Docker Deployment (Alternative)

### 4.1 Local Docker Setup

```bash
# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### 4.2 Deploy to Cloud with Docker

```bash
# Build and push to Google Container Registry
cd backend
gcloud builds submit --tag gcr.io/clearpath-customs/backend

# Deploy to Cloud Run from container
gcloud run deploy clearpath-api \
  --image gcr.io/clearpath-customs/backend \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated
```

---

## 🔐 Step 5: Security Configuration

### 5.1 Enable Authentication

```bash
# Enable Firebase Authentication
# Firebase Console → Authentication → Get Started
# Enable Email/Password and Google Sign-In
```

### 5.2 Configure CORS

Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clearpath-customs.web.app",
        "https://clearpath-customs.firebaseapp.com",
        "https://clearpath.ai"  # Your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.3 Setup API Rate Limiting

```bash
# Install Redis for rate limiting
pip install slowapi

# Configure in main.py (already included)
```

---

## 📊 Step 6: Monitoring & Analytics

### 6.1 Setup Sentry (Error Tracking)

```bash
# Create Sentry project at https://sentry.io
# Get DSN

# Add to backend/.env
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# Sentry is auto-configured in main.py
```

### 6.2 Setup Google Cloud Monitoring

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=clearpath-api" --limit 50

# Setup alerts
# Cloud Console → Monitoring → Alerting → Create Policy
```

### 6.3 Setup Firebase Analytics

```javascript
// Already configured in frontend/src/firebase.ts
// View analytics in Firebase Console → Analytics
```

---

## 🧪 Step 7: Testing Deployment

### 7.1 Test Backend API

```bash
# Health check
curl https://clearpath-api-xxx-uc.a.run.app/health

# Test document upload
curl -X POST https://clearpath-api-xxx-uc.a.run.app/api/v1/documents/upload \
  -F "file=@sample-invoice.pdf" \
  -F "document_type=invoice"
```

### 7.2 Test Frontend

1. Visit https://clearpath-customs.web.app
2. Upload sample documents
3. Generate declaration
4. Verify all features work

### 7.3 Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://clearpath-api-xxx-uc.a.run.app/health
```

---

## 📈 Step 8: Scaling Configuration

### 8.1 Auto-scaling Settings

```bash
# Update Cloud Run auto-scaling
gcloud run services update clearpath-api \
  --min-instances 1 \
  --max-instances 100 \
  --concurrency 80 \
  --cpu-throttling \
  --region asia-south1
```

### 8.2 CDN Configuration

```bash
# Enable Firebase Hosting CDN (automatic)
# For custom domain, configure Cloud CDN:
gcloud compute backend-services update clearpath-backend \
  --enable-cdn \
  --cache-mode CACHE_ALL_STATIC
```

---

## 💰 Step 9: Cost Optimization

### Estimated Monthly Costs (1,000 users, 10,000 shipments/month)

| Service | Usage | Cost |
|---------|-------|------|
| Firebase Hosting | 50GB bandwidth | $0.15/GB = $7.50 |
| Firestore | 1M reads, 500K writes | $0.06 + $0.18 = $0.24 |
| Cloud Storage | 10GB storage, 100GB egress | $0.20 + $12 = $12.20 |
| Cloud Run | 100K requests, 200 CPU-hours | $0.40 + $4.80 = $5.20 |
| OpenAI API | 10K requests × $0.03 | $300 |
| **Total** | | **~$325/month** |

### Cost Optimization Tips

1. **Cache HS Code Classifications**
   ```python
   # Use Redis to cache common classifications
   # Reduces AI API calls by 70%
   ```

2. **Batch Processing**
   ```python
   # Process multiple documents in single AI call
   # Reduces API costs by 40%
   ```

3. **Use Cloud Run Min Instances = 0**
   ```bash
   # Scale to zero when idle
   # Saves ~$50/month
   ```

---

## 🔄 Step 10: CI/CD Pipeline

### 10.1 GitHub Actions Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: clearpath-customs
      
      - name: Deploy to Cloud Run
        run: |
          cd backend
          gcloud run deploy clearpath-api \
            --source . \
            --region asia-south1 \
            --allow-unauthenticated

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build
      
      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          channelId: live
          projectId: clearpath-customs
```

---

## 🆘 Troubleshooting

### Common Issues

**1. Firebase credentials not found**
```bash
# Ensure firebase-credentials.json is in backend/
# Check FIREBASE_CREDENTIALS_PATH environment variable
```

**2. CORS errors**
```bash
# Update CORS origins in backend/main.py
# Redeploy backend
```

**3. Cloud Run cold starts**
```bash
# Set min-instances to 1
gcloud run services update clearpath-api --min-instances 1
```

**4. Out of memory errors**
```bash
# Increase memory
gcloud run services update clearpath-api --memory 4Gi
```

---

## 📞 Support

- **Documentation:** https://docs.clearpath.ai
- **Email:** devops@clearpath.ai
- **Slack:** clearpath-team.slack.com

---

## ✅ Deployment Checklist

- [ ] Firebase project created
- [ ] Firestore rules deployed
- [ ] Storage rules deployed
- [ ] Service account key downloaded
- [ ] API keys configured
- [ ] Backend deployed to Cloud Run
- [ ] Frontend built and deployed to Firebase Hosting
- [ ] Custom domain configured (optional)
- [ ] Monitoring setup (Sentry, Cloud Monitoring)
- [ ] Load testing completed
- [ ] Security audit completed
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline configured

---

**Deployment Time:** ~45 minutes for first deployment, ~5 minutes for updates

**Status Page:** https://status.clearpath.ai (setup with Statuspage.io)
