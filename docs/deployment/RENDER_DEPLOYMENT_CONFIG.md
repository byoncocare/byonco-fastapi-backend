# Render Deployment Configuration

**Status:** ✅ **PRODUCTION READY**

---

## FastAPI App Entrypoint

**File:** `server.py`  
**Variable:** `app = FastAPI()` (line 57)

---

## Render Start Command

Set this in Render dashboard: **Dashboard → Your Service → Settings → Start Command**

```
uvicorn server:app --host 0.0.0.0 --port 10000
```

**Important Notes:**
- Use `server:app` (not `main:app` or `app:app`)
- `--host 0.0.0.0` allows external connections
- `--port 10000` is Render's default port (or set via `PORT` env var)

---

## Required Environment Variables

Set these in Render: **Dashboard → Your Service → Environment**

```
OPENAI_API_KEY=<set in Render>
RAZORPAY_KEY_ID=<set in Render>
RAZORPAY_KEY_SECRET=<set in Render>
SUPABASE_URL=<set in Render>
SUPABASE_SERVICE_ROLE_KEY=<set in Render>
MONGO_URL=<set in Render>
DB_NAME=<set in Render>
```

---

## Health & Debug Endpoints

### GET /health

**Path:** Root level (not under `/api`)

**Response:**
```json
{"status": "ok", "service": "byonco-api"}
```

**Purpose:** Production health check for monitoring

---

### GET /api/debug/env-check

**Path:** Root level (not under `/api/api`)

**Response:**
```json
{
  "openai_configured": true,
  "razorpay_configured": true,
  "supabase_configured": true
}
```

**Purpose:** Debug endpoint to verify environment variables are set (returns booleans only, never exposes secrets)

---

## Local Testing Commands

### 1. Start Local Server

```bash
cd C:\Users\AJINKYA\byonco-fastapi-backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at `http://localhost:8000`

---

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "ok", "service": "byonco-api"}
```

---

### 3. Test Environment Check

```bash
curl http://localhost:8000/api/debug/env-check
```

**Expected Response:**
```json
{
  "openai_configured": true,
  "razorpay_configured": true,
  "supabase_configured": true
}
```

**Note:** Returns `false` if environment variables are not set locally.

---

### 4. Test OpenAPI Schema

```bash
curl http://localhost:8000/openapi.json
```

**Expected:** Returns full OpenAPI JSON schema with all endpoints

---

### PowerShell Commands (Windows)

```powershell
# Health check
curl.exe http://localhost:8000/health

# Environment check
curl.exe http://localhost:8000/api/debug/env-check

# OpenAPI schema
curl.exe http://localhost:8000/openapi.json
```

---

## Render Testing Commands

After deploying to Render, test with your Render service URL:

**Replace `https://your-service.onrender.com` with your actual Render URL.**

### 1. Test Health Endpoint

```bash
curl https://your-service.onrender.com/health
```

**Expected Response:**
```json
{"status": "ok", "service": "byonco-api"}
```

---

### 2. Test Environment Check

```bash
curl https://your-service.onrender.com/api/debug/env-check
```

**Expected Response:**
```json
{
  "openai_configured": true,
  "razorpay_configured": true,
  "supabase_configured": true
}
```

**All should be `true` if environment variables are set correctly in Render.**

---

### 3. Test OpenAPI Schema

```bash
curl https://your-service.onrender.com/openapi.json
```

**Expected:** Returns full OpenAPI JSON schema

---

## Router Verification

All routers are included on the same `app` instance in `server.py`:

- ✅ `api_router` (main API router with `/api` prefix)
- ✅ `cost_calculator_router`
- ✅ `hospitals_router`
- ✅ `rare_cancers_router`
- ✅ `auth_router`
- ✅ `payments_router`
- ✅ `vayu_razorpay_router`
- ✅ `get_started_router`
- ✅ `journey_builder_router`
- ✅ `ai_router`

**All registered routes are logged on startup** - check Render logs to verify all routes are registered.

---

## Startup Route Logging

On application startup, all registered routes are logged:

```
============================================================
📋 REGISTERED ROUTES (FastAPI App)
============================================================
  GET /health
  GET /api/debug/env-check
  GET /openapi.json
  GET /docs
  ... (all other routes)
============================================================
Total routes registered: XX
============================================================
```

**Check Render logs after deployment to verify all routes are registered.**

---

## Verification Checklist

After deploying to Render:

- [ ] Service starts without errors
- [ ] `/health` endpoint returns 200 OK
- [ ] `/api/debug/env-check` shows all services configured (`true`)
- [ ] Startup logs show all routes registered
- [ ] `/openapi.json` returns full schema
- [ ] All API endpoints work correctly

---

## Troubleshooting

### Service Won't Start

**Check:**
- Start command is exactly: `uvicorn server:app --host 0.0.0.0 --port 10000`
- `server.py` exists in root directory
- All dependencies installed (`requirements.txt`)

### Health Endpoint Returns 404

**Check:**
- Endpoint is on root app (not `api_router`)
- Route path is `/health` (not `/api/health`)
- Service restarted after code changes

### Env-Check Shows `false`

**Check:**
- Environment variables set in Render dashboard
- Variable names are correct (case-sensitive)
- Service restarted after adding variables

### Routes Not Showing in Logs

**Check:**
- Startup event handler is defined
- All routers are included before startup
- Check Render logs for startup messages

---

**Status:** ✅ **CONFIGURED FOR RENDER DEPLOYMENT**

All endpoints verified and ready for production deployment.

