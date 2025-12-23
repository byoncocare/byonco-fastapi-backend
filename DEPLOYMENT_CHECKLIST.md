# Deployment Checklist - Razorpay Integration

## A) Git: Prepare & Push

### Backend Repository

**Step 1: Verify .gitignore**
```powershell
cd C:\Users\AJINKYA\byonco-fastapi-backend
Get-Content .gitignore
```
✅ Should include: `.env`, `.env.*`, `venv/`, `__pycache__/`, `*.pyc`

**Step 2: Verify .env is NOT staged**
```powershell
git status | Select-String ".env"
```
✅ Should show `.env` is NOT in the list (it's ignored)

**Step 3: Stage Razorpay changes**
```powershell
git add payments/razorpay.py
git add payments/service.py
git add server.py
git add RAZORPAY_*.md
git add END_TO_END_TESTING.md
git add FINAL_FIX_SUMMARY.md
```

**Step 4: Commit**
```powershell
git commit -m "Razorpay backend payments production-ready"
```

**Step 5: Verify remote**
```powershell
git remote -v
```
✅ Should show: `origin https://github.com/byoncocare/byonco-fastapi-backend.git`

**Step 6: Push to main**
```powershell
git push origin main
```

---

### Frontend Repository

**Step 1: Navigate to frontend root**
```powershell
cd C:\Users\AJINKYA\ByOnco
```

**Step 2: Verify .gitignore includes .env**
```powershell
Get-Content .gitignore | Select-String ".env"
```
✅ Should show `.env.local`, `.env.development.local`, etc.

**Step 3: Add .env to .gitignore if missing**
```powershell
Add-Content .gitignore "`n# Environment variables`n.env`n.env.local`n"
```

**Step 4: Stage checkout/Razorpay changes**
```powershell
git add src/products/vayu/pages/VayuCheckoutPage.jsx
git add src/products/vayu/pages/VayuCheckoutSuccess.jsx
git add src/products/vayu/pages/VayuOrderPage.jsx
git add src/products/vayu/components/order/
git add src/products/vayu/utils/
git add src/App.js
```

**Step 5: Commit**
```powershell
git commit -m "Checkout flow + Razorpay integration"
```

**Step 6: Verify remote**
```powershell
git remote -v
```
✅ Should show: `origin https://github.com/byoncocare/byonco.git`

**Step 7: Push to main**
```powershell
git push origin main
```

---

## B) Render: Deploy Backend

### Step 1: Create Render Web Service

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository: `byoncocare/byonco-fastapi-backend`
4. Configure:
   - **Name**: `byonco-fastapi-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty (root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn server:app --host 0.0.0.0 --port $PORT`

### Step 2: Add Environment Variables

In Render dashboard → Your service → **Environment** tab, add:

```
RAZORPAY_KEY_ID = [PASTE YOUR RAZORPAY_KEY_ID]
RAZORPAY_KEY_SECRET = [PASTE YOUR RAZORPAY_KEY_SECRET]
SECRET_KEY = [GENERATE: See below]
MONGO_URL = [PASTE YOUR MONGO_URL - Optional if not using MongoDB]
DB_NAME = byonco
```

**Generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and use it as `SECRET_KEY` value.

### Step 3: Deploy

Click **"Save Changes"** → Render will auto-deploy

### Step 4: Get Render URL

After deployment, copy your Render URL (e.g., `https://byonco-fastapi-backend.onrender.com`)

### Step 5: Verify Deployment

**Test Health Endpoint:**
```powershell
curl.exe https://YOUR-RENDER-URL.onrender.com/api/payments/razorpay/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "razorpay_configured": true,
  "key_id_present": true
}
```

**Test Create Order:**
```powershell
curl.exe -X POST https://YOUR-RENDER-URL.onrender.com/api/payments/razorpay/create-order `
  -H "Content-Type: application/json" `
  -d '{\"productId\": \"vayu-ai-glasses\", \"variantId\": \"non-prescription\", \"quantity\": 1}'
```

**Expected Response:**
```json
{
  "orderId": "VAYU-2025-ABC123",
  "razorpayOrderId": "order_xyz789",
  "amount": 59999.0,
  "currency": "INR",
  "keyId": "rzp_test_..."
}
```

---

## C) Vercel: Deploy Frontend

### Step 1: Connect Repository

1. Go to: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import Git Repository: `byoncocare/byonco`
4. Configure:
   - **Framework Preset**: `Create React App` (or auto-detect)
   - **Root Directory**: Leave empty or set if needed
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `build` (default)

### Step 2: Add Environment Variable

In **Environment Variables** section, add:

```
REACT_APP_BACKEND_URL = https://YOUR-RENDER-URL.onrender.com
```

Replace `YOUR-RENDER-URL` with your actual Render URL from Step B.4.

### Step 3: Deploy

Click **"Deploy"** → Vercel will build and deploy

### Step 4: Get Vercel URL

After deployment, copy your Vercel URL (e.g., `https://byonco.vercel.app`)

### Step 5: Verify Deployment

1. **Visit Checkout Page:**
   ```
   https://YOUR-VERCEL-URL.vercel.app/products/vayu/checkout
   ```

2. **Test Checkout Flow:**
   - Fill in form fields
   - Click "Pay now"
   - Razorpay modal should open
   - Complete test payment
   - Should redirect to success page

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Check Network tab for API calls
   - Verify calls go to Render backend URL
   - No CORS errors

---

## D) Post-Deployment Verification

### Backend Verification

**1. Health Check:**
```powershell
curl.exe https://YOUR-RENDER-URL.onrender.com/api/payments/razorpay/health
```

**2. API Docs:**
```
https://YOUR-RENDER-URL.onrender.com/docs
```
✅ Should show Razorpay endpoints

**3. Create Order Test:**
```powershell
curl.exe -X POST https://YOUR-RENDER-URL.onrender.com/api/payments/razorpay/create-order `
  -H "Content-Type: application/json" `
  -d '{\"productId\": \"vayu-ai-glasses\", \"variantId\": \"non-prescription\", \"quantity\": 1, \"couponCode\": \"LAUNCH2025\"}'
```

### Frontend Verification

**1. Order Page:**
```
https://YOUR-VERCEL-URL.vercel.app/products/vayu/order
```
✅ Should load product page with pricing

**2. Checkout Page:**
```
https://YOUR-VERCEL-URL.vercel.app/products/vayu/checkout
```
✅ Should load checkout form

**3. End-to-End Test:**
- Add product to cart
- Go to checkout
- Fill form
- Click "Pay now"
- Complete Razorpay payment
- Should see success page

---

## Security Checklist

- [ ] `.env` file NOT committed (check `git status`)
- [ ] `.gitignore` includes `.env`, `venv/`, `__pycache__/`
- [ ] Render environment variables set (not in code)
- [ ] Vercel environment variables set (not in code)
- [ ] No secrets in logs (check Render logs)
- [ ] CORS configured correctly (allows Vercel domain)

---

## Troubleshooting

### Backend Issues

**Issue: "ModuleNotFoundError: No module named 'razorpay'"**
- Solution: Ensure `requirements.txt` includes `razorpay>=1.4.2` and `setuptools>=80.0.0`

**Issue: "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set"**
- Solution: Verify environment variables are set in Render dashboard

**Issue: CORS errors**
- Solution: Check `server.py` CORS config includes Vercel domain

### Frontend Issues

**Issue: "Failed to create order"**
- Solution: Check `REACT_APP_BACKEND_URL` is set correctly in Vercel

**Issue: Razorpay modal doesn't open**
- Solution: Check browser console for errors, verify Razorpay SDK loads

**Issue: Payment verification fails**
- Solution: Check backend logs in Render, verify signature verification logic

---

## Quick Reference

**Backend URL:** `https://YOUR-RENDER-URL.onrender.com`  
**Frontend URL:** `https://YOUR-VERCEL-URL.vercel.app`  
**Health Check:** `GET /api/payments/razorpay/health`  
**Create Order:** `POST /api/payments/razorpay/create-order`  
**Verify Payment:** `POST /api/payments/razorpay/verify`

