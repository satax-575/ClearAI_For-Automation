# 🚀 ClearPath Deployment Guide

## Complete End-to-End Deployment

### ✅ What's Included

```
clearpath-deploy/
├── README.md                    # Project overview
├── ARCHITECTURE.md              # System design
├── DEPLOYMENT.md                # Detailed deployment
├── LICENSE                      # MIT License
├── .gitignore                   # Git exclusions
├── docker-compose.yml           # Docker setup
├── firebase.json                # Firebase config
├── firestore.rules              # Database security
├── firestore.indexes.json       # Query optimization
├── storage.rules                # Storage security
├── backend/                     # Python FastAPI
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── services/
│   │   ├── ai_extractor.py
│   │   ├── compliance_engine.py
│   │   ├── hs_classifier.py
│   │   ├── carbon_calculator.py
│   │   ├── firebase_service.py
│   │   └── document_processor.py
│   └── utils/
│       └── logger.py
└── frontend/                    # React TypeScript
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── Dockerfile
    ├── index.html
    ├── .env.example
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── components/
        │   └── Header.tsx
        ├── pages/
        │   ├── Dashboard.tsx
        │   ├── UploadDocuments.tsx
        │   ├── ViewDeclaration.tsx
        │   └── Analytics.tsx
        └── services/
            └── api.ts
```

---

## 🎯 Step 1: Upload to GitHub

```bash
cd clearpath-deploy
git init
git add .
git commit -m "ClearPath Customs - Complete Platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/clearpath-customs.git
git push -u origin main
```

---

## 🔥 Step 2: Deploy Frontend to Firebase

```bash
cd frontend
npm install
npm run build
cd ..
firebase login
firebase use dp-world-hackathon-ocr
firebase deploy --only hosting
```

**Your frontend will be live at:**
https://dp-world-hackathon-ocr.web.app

---

## 🌐 Step 3: Deploy Backend to Render.com

1. Go to https://render.com
2. Sign up/Login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** clearpath-api
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. Add Environment Variables:
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   FIREBASE_PROJECT_ID=dp-world-hackathon-ocr
   FIREBASE_API_KEY=your_firebase_api_key
   ```

7. Click "Create Web Service"

8. Wait 5-10 minutes for deployment

9. Copy your API URL (e.g., `https://clearpath-api-xxxx.onrender.com`)

---

## 🔗 Step 4: Connect Frontend to Backend

1. Update `frontend/src/services/api.ts`:
   ```typescript
   const API_BASE_URL = 'https://clearpath-api-xxxx.onrender.com'
   ```

2. Rebuild and redeploy frontend:
   ```bash
   cd frontend
   npm run build
   cd ..
   firebase deploy --only hosting
   ```

---

## ✅ Step 5: Test End-to-End

1. Visit: https://dp-world-hackathon-ocr.web.app
2. Upload sample documents
3. Generate declaration
4. Verify API calls work

---

## 🎉 You're Live!

- **Frontend:** https://dp-world-hackathon-ocr.web.app
- **Backend:** https://clearpath-api-xxxx.onrender.com
- **API Docs:** https://clearpath-api-xxxx.onrender.com/api/docs

---

## 📞 Need Help?

Check DEPLOYMENT.md for detailed instructions or contact support.
