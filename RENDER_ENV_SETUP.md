# 🔧 Render Environment Variables Setup

## ⚠️ CRITICAL: MongoDB Connection Error

The backend is currently trying to connect to `localhost:27017` which doesn't exist on Render. You need to set up environment variables on Render.

## 📋 Required Environment Variables

Go to your Render Dashboard → `byonco-fastapi-backend` → **Environment** tab and add these:

### 1. MongoDB Connection (REQUIRED)
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```
**Replace with your actual MongoDB Atlas connection string**

### 2. Database Name (REQUIRED)
```
DB_NAME=byonco_db
```
Or whatever database name you're using

### 3. JWT Secret Key (REQUIRED)
```
SECRET_KEY=your-very-secure-secret-key-here-minimum-32-characters
```
**Generate a secure random string (at least 32 characters)**

### 4. CORS Origins (Optional - already in code, but can override)
```
CORS_ORIGINS=https://byoncocare.com,https://www.byoncocare.com
```

### 5. RazorPay Keys (If using payments)
```
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

## 🚀 Steps to Fix

1. **Go to Render Dashboard:**
   - https://dashboard.render.com
   - Click on `byonco-fastapi-backend` service

2. **Go to Environment Tab:**
   - Click on **"Environment"** in the left sidebar

3. **Add Environment Variables:**
   - Click **"Add Environment Variable"**
   - Add each variable listed above
   - **Most Important:** `MONGO_URL` with your MongoDB Atlas connection string

4. **Redeploy:**
   - After adding variables, Render will auto-redeploy
   - Or click **"Manual Deploy"** → **"Deploy latest commit"**

5. **Verify:**
   - Check the **"Logs"** tab
   - Should see successful MongoDB connection
   - No more "Connection refused" errors

## 🔍 How to Get MongoDB Atlas Connection String

1. Go to https://cloud.mongodb.com
2. Select your cluster
3. Click **"Connect"**
4. Choose **"Connect your application"**
5. Copy the connection string
6. Replace `<password>` with your actual password
7. Replace `<dbname>` with your database name (or remove it)

Example format:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/byonco_db?retryWrites=true&w=majority
```

## ⚠️ Important Notes

- **Never commit `.env` files to Git** (they're already in `.gitignore`)
- **Environment variables on Render are secure** - they're not visible in code
- **After adding variables, the service will restart automatically**
- **Check logs to verify MongoDB connection is successful**

## ✅ Verification

After setting up environment variables, test registration:
1. Go to https://www.byoncocare.com/auth
2. Try to register
3. Check browser console - should NOT see "Connection refused" error
4. Check Render logs - should see successful MongoDB connection

