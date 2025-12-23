# Render Deployment - Step-by-Step Guide

## Prerequisites
- GitHub repository: `byoncocare/byonco-fastapi-backend` ✅ (already pushed)
- Render account: https://dashboard.render.com

## Step 1: Create Web Service

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in or create account

2. **Create New Web Service**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

3. **Connect GitHub Repository**
   - Click **"Connect account"** if not already connected
   - Authorize Render to access GitHub
   - Search for: `byonco-fastapi-backend`
   - Click **"Connect"** next to `byoncocare/byonco-fastapi-backend`

## Step 2: Configure Service

Fill in these settings:

```
Name: byonco-fastapi-backend
Region: (Choose closest to your users - e.g., Singapore, US East)
Branch: main
Root Directory: (leave empty)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Important Settings:**
- **Auto-Deploy**: Yes (deploys on every push to main)
- **Plan**: Free (or choose paid if needed)

## Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables one by one:

### 1. RAZORPAY_KEY_ID
```
Key: RAZORPAY_KEY_ID
Value: [PASTE YOUR RAZORPAY_KEY_ID]
```

### 2. RAZORPAY_KEY_SECRET
```
Key: RAZORPAY_KEY_SECRET
Value: [PASTE YOUR RAZORPAY_KEY_SECRET]
```

### 3. SECRET_KEY
Generate a secure key first:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then add:
```
Key: SECRET_KEY
Value: [PASTE THE GENERATED KEY]
```

### 4. DB_NAME (Optional - if using MongoDB)
```
Key: DB_NAME
Value: byonco
```

### 5. MONGO_URL (Optional - if using MongoDB)
```
Key: MONGO_URL
Value: [YOUR MONGODB CONNECTION STRING]
```

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies (`pip install -r requirements.txt`)
   - Start the server
3. Wait for deployment to complete (2-5 minutes)
4. You'll see logs in real-time

## Step 5: Get Your Render URL

After successful deployment:
- Your service URL will be: `https://byonco-fastapi-backend.onrender.com`
- Or check the **"Settings"** tab for your custom domain

**Save this URL** - you'll need it for Vercel!

## Step 6: Verify Deployment

### Test Health Endpoint
```powershell
curl.exe https://byonco-fastapi-backend.onrender.com/api/payments/razorpay/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "razorpay_configured": true,
  "key_id_present": true
}
```

### Test API Docs
Visit: `https://byonco-fastapi-backend.onrender.com/docs`

Should show FastAPI Swagger UI with Razorpay endpoints.

### Test Create Order
```powershell
curl.exe -X POST https://byonco-fastapi-backend.onrender.com/api/payments/razorpay/create-order `
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

## Troubleshooting

### Build Fails
- Check logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python version is compatible

### Service Crashes
- Check logs for errors
- Verify environment variables are set
- Check `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are correct

### Health Check Returns `razorpay_configured: false`
- Verify environment variables in Render dashboard
- Check variable names are exact (case-sensitive)
- Redeploy after adding variables

## Next Step
Once Render is deployed, proceed to Vercel deployment (see `VERCEL_DEPLOY_STEPS.md`)

