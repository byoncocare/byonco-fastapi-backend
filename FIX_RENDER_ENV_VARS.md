# Fix Render Environment Variables - Step by Step

## Current Issue
Backend returns 500 error because `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are missing.

## Step-by-Step Fix

### Step 1: Open Render Environment Settings

1. In Render dashboard (where you are now)
2. Click **"Environment"** in the left sidebar (under "MANAGE" section)
3. You should see a list of environment variables

### Step 2: Add RAZORPAY_KEY_ID

1. Click **"Add Environment Variable"** button
2. Fill in:
   ```
   Key: RAZORPAY_KEY_ID
   Value: [PASTE YOUR RAZORPAY KEY ID]
   ```
3. Click **"Save"**

### Step 3: Add RAZORPAY_KEY_SECRET

1. Click **"Add Environment Variable"** again
2. Fill in:
   ```
   Key: RAZORPAY_KEY_SECRET
   Value: [PASTE YOUR RAZORPAY KEY SECRET]
   ```
3. Click **"Save"**

### Step 4: Verify Variables Are Set

You should see both variables in the list:
- ✅ RAZORPAY_KEY_ID
- ✅ RAZORPAY_KEY_SECRET

### Step 5: Render Will Auto-Redeploy

- After saving, Render will automatically redeploy (1-2 minutes)
- Watch the "Events" tab to see deployment progress
- Wait for "Deploy live" status

### Step 6: Test

After deployment completes, test:

```powershell
curl.exe https://byonco-fastapi-backend.onrender.com/api/payments/razorpay/health
```

Should return:
```json
{"status":"ok","razorpay_configured":true,"key_id_present":true}
```

## If You Don't Have Razorpay Keys Yet

### Get Razorpay Test Keys:

1. Go to: https://dashboard.razorpay.com
2. Sign in (or create free account)
3. Go to: **Settings** → **API Keys**
4. Click **"Generate Test Keys"**
5. Copy:
   - **Key ID** (starts with `rzp_test_`)
   - **Key Secret** (long string)
6. Use these in Render

## Complete Environment Variables Checklist

Make sure ALL these are set in Render:

```
✅ RAZORPAY_KEY_ID = [Your Key ID]
✅ RAZORPAY_KEY_SECRET = [Your Key Secret]
✅ SECRET_KEY = O23uBe1y-GJLPsuggYGp5-PrTOVZe9ZZ7dFok4QgSKg
✅ MONGO_URL = [Your MongoDB URL - if using]
✅ DB_NAME = byonco
```

## After Adding Keys

1. Wait for Render to redeploy (check Events tab)
2. Test checkout page again
3. "Pay now" button should work! 🎉

