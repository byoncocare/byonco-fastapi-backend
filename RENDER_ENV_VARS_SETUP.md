# Render Environment Variables Setup - URGENT

## ❌ Current Issue
Backend is returning error:
```
Configuration error - RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set in environment variables
```

## ✅ Fix: Add Environment Variables in Render

### Step 1: Go to Render Dashboard
https://dashboard.render.com

### Step 2: Open Your Service
Click on: `byonco-fastapi-backend`

### Step 3: Go to Environment Tab
In left sidebar, click: **"Environment"**

### Step 4: Add These Variables

Click **"Add Environment Variable"** and add:

**Variable 1:**
```
Key: RAZORPAY_KEY_ID
Value: [YOUR RAZORPAY KEY ID]
```

**Variable 2:**
```
Key: RAZORPAY_KEY_SECRET
Value: [YOUR RAZORPAY KEY SECRET]
```

### Step 5: Save & Redeploy
- Click **"Save Changes"** (top right)
- Render will automatically redeploy (1-2 minutes)

### Step 6: Verify

After redeploy, test:

```powershell
curl.exe https://byonco-fastapi-backend.onrender.com/api/payments/razorpay/health
```

Should return:
```json
{
  "status": "ok",
  "razorpay_configured": true,
  "key_id_present": true
}
```

## Where to Get Razorpay Keys

1. Go to: https://dashboard.razorpay.com
2. Sign in or create account
3. Settings → **API Keys**
4. Generate **Test Keys** (for testing) or **Live Keys** (for production)
5. Copy:
   - **Key ID** → Use as `RAZORPAY_KEY_ID`
   - **Key Secret** → Use as `RAZORPAY_KEY_SECRET`

## Important Notes

- ✅ Environment variables are case-sensitive
- ✅ Do NOT include quotes around values
- ✅ Keys are secret - never commit them
- ✅ Test keys start with `rzp_test_`
- ✅ Live keys start with `rzp_live_`

## Complete Environment Variables Checklist

Make sure ALL these are set in Render:

```
✅ RAZORPAY_KEY_ID = [Your Razorpay Key ID]
✅ RAZORPAY_KEY_SECRET = [Your Razorpay Key Secret]
✅ SECRET_KEY = O23uBe1y-GJLPsuggYGp5-PrTOVZe9ZZ7dFok4QgSKg
✅ MONGO_URL = [Your MongoDB URL - if using]
✅ DB_NAME = byonco
```

After adding Razorpay keys, the checkout will work! 🎉

