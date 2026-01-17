# Render Environment Variables Configuration

## Required Environment Variables

Set these in Render dashboard: **Dashboard → Your Service → Environment**

```
OPENAI_API_KEY=<set in Render>
RAZORPAY_KEY_ID=<set in Render>
RAZORPAY_KEY_SECRET=<set in Render>
SUPABASE_URL=<set in Render>
SUPABASE_SERVICE_ROLE_KEY=<set in Render>
MONGO_URL=<set in Render> (optional, if using MongoDB)
DB_NAME=<set in Render> (optional, if using MongoDB)
```

---

## How to Set Environment Variables in Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service (e.g., `byonco-fastapi-backend`)
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add each variable:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `<your actual key from OpenAI dashboard>`
   - Click **Save Changes**
6. Repeat for all variables
7. Service will automatically restart after saving

---

## How to Get Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy the key (starts with `sk-`)
4. **Important:** Save immediately - key shown only once
5. **Never commit the key to git or documentation**

### Razorpay Keys
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Settings → API Keys
3. Copy **Key ID** (starts with `rzp_test_` or `rzp_live_`)
4. Copy **Key Secret** (your secret key from dashboard)
5. **Important:** Use test keys for staging, live keys for production
6. **Never commit the secret key to git or documentation**

### Supabase Keys
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Settings → API
4. Copy **Project URL** (format: `https://xxx.supabase.co`)
5. Copy **service_role** key (NOT anon key)
   - Look for "service_role" secret in the API settings
   - **Warning:** This key has admin access - keep it secret!
   - **Never commit the service_role key to git or documentation**

### MongoDB (Optional)
1. If using MongoDB, get connection string from MongoDB Atlas
2. Format: `mongodb+srv://username:password@cluster.mongodb.net/dbname`

---

## Verify Environment Variables Are Set

After setting variables, test the env-check endpoint:

```bash
curl https://your-backend.onrender.com/api/debug/env-check
```

**Expected Response:**
```json
{
  "openai_configured": true,
  "razorpay_configured": true,
  "supabase_configured": true
}
```

If any value is `false`, check:
- ✅ Variable name is exactly correct (case-sensitive)
- ✅ Value is copied correctly (no extra spaces)
- ✅ Service was restarted after adding variables
- ✅ You're using service_role key for Supabase (not anon key)

---

## Security Notes

### ✅ DO:
- ✅ Store all keys in Render environment variables (never in code)
- ✅ Use service_role key for backend (has admin access)
- ✅ Use test keys for staging/testing
- ✅ Use live keys only in production
- ✅ Rotate keys periodically
- ✅ Monitor usage for suspicious activity

### ❌ DON'T:
- ❌ Commit keys to git
- ❌ Share keys in chat/email
- ❌ Use anon key on backend (use service_role)
- ❌ Use live keys in development
- ❌ Hardcode keys in source code
- ❌ Log keys in application logs

---

## Key Rotation

If you need to rotate keys:

1. **Generate new key** from provider dashboard
2. **Update in Render** environment variables
3. **Test endpoints** to verify new key works
4. **Revoke old key** from provider dashboard (after confirming new key works)

---

## Troubleshooting

### Env-check returns false

**Problem:** `openai_configured: false`

**Solution:**
- Check `OPENAI_API_KEY` is set in Render
- Verify key format is correct
- Check for typos in variable name

**Problem:** `razorpay_configured: false`

**Solution:**
- Check both `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set
- Verify key ID starts with `rzp_test_` or `rzp_live_`
- Check for typos in variable names

**Problem:** `supabase_configured: false`

**Solution:**
- Check both `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Verify URL format: `https://xxx.supabase.co`
- Verify you're using service_role key (not anon key)
- Check for typos in variable names

---

## Production vs Staging

### Staging (Testing)
- Use Razorpay test keys (`rzp_test_...`)
- Use OpenAI API key (same for both)
- Use Supabase service_role key (same for both)

### Production
- Use Razorpay live keys (`rzp_live_...`)
- Use OpenAI API key (same)
- Use Supabase service_role key (same)

**Note:** Consider using separate Supabase projects for staging/production for better isolation.

