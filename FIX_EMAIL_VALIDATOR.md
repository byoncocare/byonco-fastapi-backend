# Fix: email-validator Not Installing

## Issue
The `email-validator` package is in `requirements.txt` but Render isn't installing it, likely due to build cache.

## Solution: Clear Build Cache

1. **Go to Render Dashboard:**
   - Navigate to: https://dashboard.render.com
   - Select service: `byonco-fastapi-backend`

2. **Clear Build Cache:**
   - Go to **Settings** tab
   - Scroll down to find **"Clear build cache"** button
   - Click **"Clear build cache"**
   - Confirm the action

3. **Redeploy:**
   - Go to **Events** tab
   - Click **"Manual Deploy"** → **"Deploy latest commit"**
   - Wait 3-5 minutes

## Alternative: Force Rebuild

If clearing cache doesn't work, try:
- In Render dashboard → Settings
- Temporarily change Build Command to: `pip install --no-cache-dir -r requirements.txt`
- Deploy
- Change it back to: `pip install -r requirements.txt`
- Deploy again

## Verify Installation

After deployment, check logs for:
```
Collecting email-validator==2.3.0
Installing collected packages: ... email-validator ...
Successfully installed email-validator-2.3.0
```

If you still see the error, the package should be installed. The issue might be elsewhere.



