# Quick Deployment Guide

## 🚀 Step-by-Step Commands

### A) Git: Commit & Push

#### Backend (FastAPI)

```powershell
# Navigate to backend
cd C:\Users\AJINKYA\byonco-fastapi-backend

# Verify .env is NOT tracked
git status | Select-String ".env"
# Should show nothing (or "nothing to commit")

# Stage Razorpay files
git add payments/razorpay.py payments/service.py server.py
git add RAZORPAY_*.md END_TO_END_TESTING.md FINAL_FIX_SUMMARY.md DEPLOYMENT_CHECKLIST.md
git add .gitignore requirements.txt

# Commit
git commit -m "Razorpay backend payments production-ready"

# Push
git push origin main
```

#### Frontend (React)

```powershell
# Navigate to frontend root
cd C:\Users\AJINKYA\ByOnco

# Stage checkout files
git add src/products/vayu/pages/VayuCheckoutPage.jsx
git add src/products/vayu/pages/VayuCheckoutSuccess.jsx
git add src/products/vayu/pages/VayuOrderPage.jsx
git add src/products/vayu/components/order/
git add src/products/vayu/utils/
git add src/App.js
git add .gitignore

# Commit
git commit -m "Checkout flow + Razorpay integration"

# Push
git push origin main
```

---

## B) Render: Deploy Backend

### 1. Create Web Service
- Go to: https://dashboard.render.com
- **New +** → **Web Service**
- Connect: `byoncocare/byonco-fastapi-backend`

### 2. Configuration
```
Name: byonco-fastapi-backend
Region: (choose closest)
Branch: main
Root Directory: (leave empty)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn server:app --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables
Add these in Render dashboard:

```
RAZORPAY_KEY_ID = [PASTE YOUR KEY]
RAZORPAY_KEY_SECRET = [PASTE YOUR SECRET]
SECRET_KEY = [GENERATE BELOW]
MONGO_URL = [YOUR MONGO URL - Optional]
DB_NAME = byonco
```

**Generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy & Get URL
- Click **Save Changes**
- Wait for deployment
- Copy your Render URL: `https://YOUR-APP.onrender.com`

### 5. Verify Backend
```powershell
# Replace YOUR-APP with your Render app name
curl.exe https://YOUR-APP.onrender.com/api/payments/razorpay/health
```

**Expected:**
```json
{"status":"ok","razorpay_configured":true,"key_id_present":true}
```

---

## C) Vercel: Deploy Frontend

### 1. Create Project
- Go to: https://vercel.com/dashboard
- **Add New...** → **Project**
- Import: `byoncocare/byonco`

### 2. Configuration
```
Framework Preset: Create React App
Root Directory: (leave empty)
Build Command: npm run build
Output Directory: build
```

### 3. Environment Variable
Add:
```
REACT_APP_BACKEND_URL = https://YOUR-APP.onrender.com
```
(Replace `YOUR-APP` with your Render URL from Step B.4)

### 4. Deploy
- Click **Deploy**
- Wait for build
- Copy Vercel URL: `https://YOUR-APP.vercel.app`

### 5. Verify Frontend
Visit:
```
https://YOUR-APP.vercel.app/products/vayu/checkout
```

---

## ✅ Verification Checklist

- [ ] Backend health endpoint returns `razorpay_configured: true`
- [ ] Backend `/docs` shows Razorpay endpoints
- [ ] Frontend checkout page loads
- [ ] "Pay now" button opens Razorpay modal
- [ ] Payment completes successfully
- [ ] Success page shows after payment

---

## 🔒 Security Checklist

- [ ] `.env` NOT in git (check `git status`)
- [ ] `.gitignore` includes `.env`, `venv/`, `__pycache__/`
- [ ] Render env vars set (not in code)
- [ ] Vercel env vars set (not in code)
- [ ] No secrets in logs

---

## 🆘 Troubleshooting

**Backend: "ModuleNotFoundError: razorpay"**
→ Check `requirements.txt` has `razorpay==1.4.2` and `setuptools>=80.0.0`

**Backend: "RAZORPAY_KEY_ID must be set"**
→ Verify env vars in Render dashboard

**Frontend: "Failed to create order"**
→ Check `REACT_APP_BACKEND_URL` in Vercel matches Render URL

**CORS errors**
→ Backend CORS already configured in `server.py` (includes Vercel domains)

---

## 📝 Quick Reference

**Backend Repo:** `byoncocare/byonco-fastapi-backend`  
**Frontend Repo:** `byoncocare/byonco`  
**Backend URL:** `https://YOUR-APP.onrender.com`  
**Frontend URL:** `https://YOUR-APP.vercel.app`

**Endpoints:**
- Health: `GET /api/payments/razorpay/health`
- Create: `POST /api/payments/razorpay/create-order`
- Verify: `POST /api/payments/razorpay/verify`

