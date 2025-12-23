# 🚀 Quick Deployment Start Guide

## ✅ What's Already Done

- ✅ Code pushed to GitHub (both repos)
- ✅ `.gitignore` configured (secrets protected)
- ✅ Configuration files created

## 📋 What You Need to Do

### 1. Deploy Backend to Render (5 minutes)

**Go to:** https://dashboard.render.com

**Steps:**
1. Click **"New +"** → **"Web Service"**
2. Connect: `byoncocare/byonco-fastapi-backend`
3. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `python -m uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   ```
   RAZORPAY_KEY_ID = [YOUR KEY]
   RAZORPAY_KEY_SECRET = [YOUR SECRET]
   SECRET_KEY = [SEE BELOW]
   DB_NAME = byonco
   ```
5. Generate SECRET_KEY (run this command):
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
6. Click **"Create Web Service"**
7. Wait for deployment (2-5 min)
8. **Copy your Render URL:** `https://YOUR-APP.onrender.com`

**Detailed guide:** See `RENDER_DEPLOY_STEPS.md`

---

### 2. Deploy Frontend to Vercel (5 minutes)

**Go to:** https://vercel.com/dashboard

**Steps:**
1. Click **"Add New..."** → **"Project"**
2. Import: `byoncocare/byonco`
3. Add Environment Variable:
   ```
   REACT_APP_BACKEND_URL = https://YOUR-RENDER-APP.onrender.com
   ```
   (Use the Render URL from Step 1.8)
4. Click **"Deploy"**
5. Wait for deployment (2-5 min)
6. **Copy your Vercel URL:** `https://YOUR-APP.vercel.app`

**Detailed guide:** See `VERCEL_DEPLOY_STEPS.md`

---

### 3. Verify Everything Works

**Backend Health:**
```powershell
curl.exe https://YOUR-RENDER-APP.onrender.com/api/payments/razorpay/health
```

**Frontend Checkout:**
Visit: `https://YOUR-VERCEL-APP.vercel.app/products/vayu/checkout`

**Test Payment:**
- Fill form → Click "Pay now"
- Use test card: `4111 1111 1111 1111`
- Complete payment → Should see success page

---

## 🔑 Required Values

You'll need to paste these in Render:

1. **RAZORPAY_KEY_ID** - From your Razorpay dashboard
2. **RAZORPAY_KEY_SECRET** - From your Razorpay dashboard  
3. **SECRET_KEY** - Generate with command above

---

## 📚 Full Documentation

- `RENDER_DEPLOY_STEPS.md` - Complete Render guide
- `VERCEL_DEPLOY_STEPS.md` - Complete Vercel guide
- `DEPLOYMENT_CHECKLIST.md` - Full checklist
- `QUICK_DEPLOY.md` - Quick reference

---

## ⚡ Quick Commands

**Generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Test Backend:**
```powershell
curl.exe https://YOUR-RENDER-APP.onrender.com/api/payments/razorpay/health
```

**Test Create Order:**
```powershell
curl.exe -X POST https://YOUR-RENDER-APP.onrender.com/api/payments/razorpay/create-order `
  -H "Content-Type: application/json" `
  -d '{\"productId\": \"vayu-ai-glasses\", \"variantId\": \"non-prescription\", \"quantity\": 1}'
```

---

## 🆘 Need Help?

- Check Render logs: Dashboard → Your Service → Logs
- Check Vercel logs: Dashboard → Your Project → Deployments → View Logs
- Verify environment variables are set correctly
- Check browser console for frontend errors

