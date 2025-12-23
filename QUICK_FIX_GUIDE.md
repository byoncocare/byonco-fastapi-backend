# 🚨 Quick Fix: Add Razorpay Keys to Render

## The Problem
Your backend is returning 500 errors because Razorpay keys are missing.

## The Solution (2 minutes)

### Option A: If You Have Razorpay Keys

1. **In Render Dashboard:**
   - Click **"Environment"** (left sidebar)
   - Click **"Add Environment Variable"**
   - Add:
     ```
     Key: RAZORPAY_KEY_ID
     Value: [YOUR KEY ID]
     ```
   - Click **"Save"**
   - Add again:
     ```
     Key: RAZORPAY_KEY_SECRET
     Value: [YOUR KEY SECRET]
     ```
   - Click **"Save"**
   - Wait 1-2 minutes for auto-redeploy

2. **Test:**
   ```powershell
   curl.exe https://byonco-fastapi-backend.onrender.com/api/payments/razorpay/health
   ```
   Should return: `{"razorpay_configured":true}`

3. **Try checkout again** - should work! ✅

---

### Option B: If You Need to Get Razorpay Keys

1. **Create Razorpay Account:**
   - Go to: https://dashboard.razorpay.com
   - Sign up (free)
   - Verify email

2. **Get Test Keys:**
   - Go to: **Settings** → **API Keys**
   - Click **"Generate Test Keys"**
   - Copy **Key ID** and **Key Secret**

3. **Add to Render** (follow Option A above)

---

## What You Should See After Fix

✅ Health check returns: `razorpay_configured: true`  
✅ Checkout page: "Pay now" opens Razorpay modal  
✅ No more 500 errors in Network tab

---

## Need Help?

Check Render logs:
- Click **"Logs"** in left sidebar
- Look for: `✅ Included vayu_razorpay_router`
- Should NOT see: `Configuration error - RAZORPAY_KEY_ID...`

