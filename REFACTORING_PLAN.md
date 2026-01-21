# Backend Refactoring Plan - Production-Grade Structure

## Current Structure Analysis

### Root Level Files (Cluttered)
- `server.py` - Main FastAPI app entry point
- `data_seed.py` - Seed data (HOSPITALS, DOCTORS, CITIES, etc.)
- `email_service.py` - Email service utility
- Multiple `.md` docs (15+ files)
- Multiple test/verification scripts
- Multiple export scripts (export_seed_data*.py)
- Legacy: `server_old.py`, `backend/` folder

### Feature Modules (Well Organized)
- `ai/`, `auth/`, `cost_calculator/`, `get_started/`, `hospitals/`, `journey_builder/`, `payments/`, `rare_cancers/`, `second_opinion/`, `waitlist/`, `whatsapp/`

### Scripts Folder
- `scripts/create_admin_user.py`
- `scripts/register_whatsapp_number.py`

## Proposed New Structure

```
byonco-fastapi-backend/
├── app/                          # Main application package (ALL runtime code)
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry (renamed from server.py)
│   ├── config.py                 # Environment/config management
│   ├── database.py               # MongoDB connection setup
│   ├── core/                     # Core utilities & shared code
│   │   ├── __init__.py
│   │   ├── models.py             # Shared Pydantic models (from server.py)
│   │   └── email_service.py      # Email service (moved from root)
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── v1/                   # API versioning
│   │   │   ├── __init__.py
│   │   │   └── router.py         # Main API router (from server.py api_router)
│   │   └── modules/              # Feature modules (move existing folders here)
│   │       ├── __init__.py
│   │       ├── ai/
│   │       ├── auth/
│   │       ├── cost_calculator/
│   │       ├── get_started/
│   │       ├── hospitals/
│   │       ├── journey_builder/
│   │       ├── payments/
│   │       ├── rare_cancers/
│   │       ├── second_opinion/
│   │       ├── waitlist/
│   │       └── whatsapp/
│   └── data/                     # Seed data
│       ├── __init__.py
│       └── seed_data.py          # Renamed from data_seed.py
├── scripts/                      # Operational scripts (organized by purpose)
│   ├── admin/
│   │   ├── create_admin_user.py
│   │   └── register_whatsapp_number.py
│   ├── seeding/
│   │   ├── export_seed_data.py
│   │   ├── export_seed_data_v2.py
│   │   ├── seed_database.py      # From cost_calculator/
│   │   └── supabase_seed.py
│   ├── testing/
│   │   ├── test_endpoints.py
│   │   ├── test_new_modules.py
│   │   └── test_server.py
│   └── verification/
│       └── verify_routes.py
├── docs/                         # Documentation (organized by category)
│   ├── deployment/
│   │   ├── GO_LIVE_CHECKLIST.md
│   │   ├── RENDER_DEPLOYMENT_CONFIG.md
│   │   ├── RENDER_ENV_VARS.md
│   │   ├── BACKEND_GO_LIVE_COMPLETE.md
│   │   └── BACKEND_GO_LIVE_SUMMARY.md
│   ├── operations/
│   │   ├── KEY_ROTATION_CHECKLIST.md
│   │   ├── PRODUCTION_SEED_EXECUTION.md
│   │   ├── PRODUCTION_HEALTH_SETUP_COMPLETE.md
│   │   ├── QUICK_START_SEEDING.md
│   │   ├── QUICK_TEST_AFTER_ROTATION.md
│   │   ├── QUICK_TEST_COMMANDS.md
│   │   ├── SEEDING_GUIDE.md
│   │   └── SECURITY_FIX_COMPLETE.md
│   └── guides/
│       ├── README_MODULES.md
│       └── SYNC_COMPLETE.md
├── archive/                      # Legacy files (preserved, not deleted)
│   ├── server_old.py
│   ├── export_seed_data_old.py
│   └── backend/                  # Old backend folder if exists
├── requirements.txt
├── README.md                     # Main project README
├── .env.example                  # Example env file
├── Makefile                      # Unix commands
└── scripts/run.ps1               # Windows PowerShell run script

```

## Migration Strategy

### Phase 1: Create New Structure (No Logic Changes)
1. Create `app/` directory and subdirectories
2. Create `scripts/` subdirectories (admin, seeding, testing, verification)
3. Create `docs/` subdirectories (deployment, operations, guides)
4. Create `archive/` directory

### Phase 2: Move Core Files
1. Move `server.py` → `app/main.py` (update imports)
2. Move `email_service.py` → `app/core/email_service.py`
3. Move `data_seed.py` → `app/data/seed_data.py`
4. Extract shared models from `server.py` → `app/core/models.py`
5. Create `app/config.py` for env management
6. Create `app/database.py` for MongoDB connection

### Phase 3: Move Feature Modules
1. Move all feature folders (`ai/`, `auth/`, etc.) → `app/api/modules/`
2. Update all imports in moved modules
3. Update imports in `app/main.py`

### Phase 4: Move Scripts & Docs
1. Move scripts to organized subdirectories
2. Move docs to organized subdirectories
3. Move legacy files to `archive/`

### Phase 5: Create Compatibility Shims (If Needed)
- Create `data_seed.py` shim that imports from `app.data.seed_data`
- Create `email_service.py` shim that imports from `app.core.email_service`
- Update any external scripts that import from old locations

### Phase 6: Update Entry Point & Create Run Scripts
1. Update `app/main.py` to be importable as `app.main:app`
2. Create `Makefile` and `scripts/run.ps1`
3. Update `README.md` with new structure

## Safety Checks

### Before Migration
- [ ] Document all router prefixes and paths
- [ ] Document all import patterns
- [ ] Create backup branch

### During Migration
- [ ] After each phase, verify imports work
- [ ] After each phase, verify routes still mount correctly
- [ ] Test server startup after each phase

### After Migration
- [ ] Run all test scripts
- [ ] Verify all API endpoints respond correctly
- [ ] Check Render deployment still works
- [ ] Verify environment variables still work

## Backward Compatibility

### Import Shims (Temporary)
- `data_seed.py` → `from app.data.seed_data import *`
- `email_service.py` → `from app.core.email_service import EmailService`

### Path Compatibility
- All API routes remain identical (`/api/*`, `/api/hospitals/*`, etc.)
- Environment variables unchanged
- Database connection unchanged

## Implementation Order

1. **Step 1**: Create new folder structure (empty directories)
2. **Step 2**: Move `data_seed.py` → `app/data/seed_data.py` + create shim
3. **Step 3**: Move `email_service.py` → `app/core/email_service.py` + create shim
4. **Step 4**: Extract models/config/database from `server.py` → separate files
5. **Step 5**: Move `server.py` → `app/main.py` + update imports
6. **Step 6**: Move feature modules → `app/api/modules/` + update imports
7. **Step 7**: Move scripts → organized subdirectories
8. **Step 8**: Move docs → organized subdirectories
9. **Step 9**: Move legacy files → `archive/`
10. **Step 10**: Create run scripts + update README

## Testing Plan

After each step:
1. Run `python -m app.main` (or equivalent) to verify imports
2. Check that FastAPI app initializes without errors
3. Verify router includes work correctly
4. Run a simple API test (e.g., `GET /api/`)

Final verification:
1. Run all test scripts in `scripts/testing/`
2. Run verification script
3. Test a few key endpoints manually
4. Verify Render deployment config still works
