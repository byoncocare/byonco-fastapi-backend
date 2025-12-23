# 🚀 Backend Deployment Guide

## ✅ Migration Complete

The backend code has been successfully migrated from `ByOnco/backend` to `byonco-fastapi-backend`.

## 📁 New Structure

```
byonco-fastapi-backend/
├── .git/                    # Git repository
├── .gitignore              # Git ignore rules
├── .env                    # Environment variables (NOT in Git)
├── README.md               # Project README
├── README_MODULES.md       # Module documentation
├── requirements.txt        # Python dependencies
├── server.py              # ⭐ Main FastAPI entrypoint
├── data_seed.py           # Seed data
├── auth/                  # Authentication module
├── cost_calculator/       # Cost calculator module
├── get_started/          # Get started module
├── hospitals/            # Hospitals module
├── payments/             # Payments module
├── rare_cancers/         # Rare cancers module
└── tests/                # Test files
```

## 🔧 Render Configuration

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
python -m uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Root Directory
Leave empty (or set to `.`)

## 🌐 CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:3000` (local dev)
- `http://localhost:5173` (local dev)
- `https://byoncocare.com` (production)
- `https://www.byoncocare.com` (production)
- `https://byonco.onrender.com` (old frontend)
- `https://byonco-*.vercel.app` (Vercel preview domains - regex pattern)

## 📍 API Endpoints

### Main Routes
- `GET /` - Root endpoint (shows registered routes)
- `GET /api/cancer-types` - Get all cancer types
- `GET /api/rare-cancers` - Get all rare cancers
- `GET /api/rare-cancers/{cancer_name}` - Get specific rare cancer
- `GET /api/hospitals` - Get hospitals
- `GET /api/cities` - Get cities
- `GET /api/doctors` - Get doctors

### Other Routes
- `/api/cost-calculator/*` - Cost calculator endpoints
- `/api/auth/*` - Authentication endpoints
- `/api/payments/*` - Payment endpoints
- `/api/get-started/*` - Get started endpoints

## 🔐 Environment Variables (Render)

Make sure these are set in Render dashboard:

- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `EMERGENT_LLM_KEY` - (Optional) LLM API key
- `JWT_SECRET` - (Optional) JWT secret for auth
- `RAZORPAY_KEY_ID` - (Optional) Razorpay key
- `RAZORPAY_KEY_SECRET` - (Optional) Razorpay secret
- `STRIPE_SECRET_KEY` - (Optional) Stripe secret

## ✅ Verification Steps

1. **After deployment, check:**
   - Visit `https://byonco-fastapi-backend.onrender.com/` - Should show route list
   - Visit `https://byonco-fastapi-backend.onrender.com/docs` - Should show Swagger UI
   - Test endpoint: `https://byonco-fastapi-backend.onrender.com/api/cancer-types`

2. **Check logs for:**
   - ✅ "Application startup complete"
   - ✅ No import errors
   - ✅ No "Could not import module" errors

3. **Test from frontend:**
   - Frontend should connect without CORS errors
   - `/api/cancer-types` should return data
   - `/api/rare-cancers` should return data

## 🐛 Troubleshooting

### "Could not import module 'server'"
- ✅ Fixed: `server.py` is now at repo root
- ✅ Start command: `python -m uvicorn server:app --host 0.0.0.0 --port $PORT`

### "404 Not Found" for `/api/cancer-types`
- ✅ Fixed: Routes are registered in `server.py`
- ✅ Check that all routers are included: `app.include_router(...)`

### CORS Errors
- ✅ Fixed: CORS middleware configured with Vercel preview domain regex
- ✅ Check `allow_origin_regex` in `server.py`

### Import Errors
- ✅ Fixed: All modules copied to repo root
- ✅ Imports use relative paths (e.g., `from rare_cancers.api_routes import ...`)

## 📝 Git Commands

After making changes:

```bash
cd C:\Users\AJINKYA\byonco-fastapi-backend
git status
git add .
git commit -m "chore: migrate FastAPI backend from ByOnco/backend"
git push origin main
```

Then in Render:
1. Go to dashboard → `byonco-fastapi-backend` service
2. Click "Manual Deploy" → "Deploy latest commit"
3. Wait 3-5 minutes
4. Check logs for success









