# Production Seeding Execution Guide
**Project:** byonco-health  
**URL:** https://thdpfewpikvunfyllmwj.supabase.co  
**Date:** 2025-01-27

---

## ✅ PHASE A - Current State (COMPLETE)

### Files Verified:
- ✅ `supabase_seed.py` - Reads `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from env
- ✅ `export_seed_data.py` - Exports 51 hospitals, 405 doctors
- ✅ `seed_exports/hospitals.json` - 51 hospitals ready
- ✅ `seed_exports/doctors.json` - 405 doctors ready
- ✅ Seeder uses **upsert mode** (safe to rerun)
- ✅ Batch size: **50 rows**, sleep: **0.25s**

---

## ✅ PHASE B - Configuration Fixed

### Fixed:
- ✅ `byonco-main/env.json` - Function URLs updated to `thdpfewpikvunfyllmwj.supabase.co`
- ✅ Flutter app hardcoded fallbacks already use correct URL

---

## ⚠️ PHASE C - Run Migrations (USER ACTION REQUIRED)

### Step 1: Check Existing Tables

**Run in Supabase SQL Editor:**

```sql
-- Check which required tables exist
SELECT 
    table_name,
    CASE 
        WHEN table_name IN ('hospitals', 'doctors', 'bed_inventory', 'queue_snapshots', 
                           'builder_plans', 'cost_estimates', 'second_opinion_requests', 
                           'reports', 'appointments', 'profiles') 
        THEN '✅ REQUIRED'
        ELSE '⚠️ OPTIONAL'
    END as status
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name IN ('hospitals', 'doctors', 'bed_inventory', 'queue_snapshots', 
                       'builder_plans', 'cost_estimates', 'second_opinion_requests', 
                       'reports', 'appointments', 'profiles')
ORDER BY table_name;
```

### Step 2: Apply Missing Tables Migration

**Run in Supabase SQL Editor:**

Copy and paste the entire contents of:
`byonco-main/supabase/migrations/20250127000001_create_missing_tables.sql`

This will create:
- `cost_estimates` (if missing)
- `second_opinion_requests` (if missing)
- Add `tier` column to `hospitals` (if missing)

**Also run builder_plans migration if not already applied:**
`byonco-main/supabase/migrations/20250127000000_create_builder_plans_table.sql`

---

## ⚠️ PHASE D - Seed Data (USER ACTION REQUIRED)

### Step 1: Set Environment Variables (PowerShell)

```powershell
cd "C:\Users\AJINKYA\byonco-fastapi-backend"

# Set correct Supabase URL
$env:SUPABASE_URL="https://thdpfewpikvunfyllmwj.supabase.co"

# USER MUST PASTE SERVICE ROLE KEY HERE:
# Get it from: Supabase Dashboard → Settings → API → service_role key
$env:SUPABASE_SERVICE_ROLE_KEY="PASTE_YOUR_SERVICE_ROLE_KEY_HERE"

# Verify they're set
Write-Host "SUPABASE_URL: $env:SUPABASE_URL"
Write-Host "SUPABASE_SERVICE_ROLE_KEY: $($env:SUPABASE_SERVICE_ROLE_KEY.Substring(0,20))..." 
```

### Step 2: Validate Python Environment

```powershell
python --version
pip show requests

# If requests not installed:
pip install requests
```

### Step 3: Re-export Data (if needed)

```powershell
# Only if seed_exports are outdated or missing
python export_seed_data.py
```

### Step 4: Run Seeder

```powershell
python supabase_seed.py
```

**Expected Success Output:**
```
[INFO] Supabase URL: https://thdpfewpikvunfyllmwj.supabase.co
[INFO] Seed dir: C:\Users\AJINKYA\byonco-fastapi-backend\seed_exports

[SEED] hospitals: 51 rows from ...\hospitals.json
[OK] hospitals batch 1/2 inserted (50/51)
[OK] hospitals batch 2/2 inserted (51/51)

[SEED] doctors: 405 rows from ...\doctors.json
[OK] doctors batch 1/9 inserted (50/405)
[OK] doctors batch 2/9 inserted (100/405)
...
[OK] doctors batch 9/9 inserted (405/405)

✅ Done. Next: run verification SQL queries in Supabase SQL Editor.
```

### Step 5: Error Troubleshooting

**If you get 401/403:**
- Verify `SUPABASE_SERVICE_ROLE_KEY` is the **service_role** key (not anon key)
- Check key has no extra spaces

**If you get 404:**
- Verify `SUPABASE_URL` is exactly `https://thdpfewpikvunfyllmwj.supabase.co`
- Check table names match exactly (hospitals, doctors)

**If you get 429 (rate limit):**
- Increase sleep time: `$env:SLEEP_SEC="0.5"`
- Reduce batch size: `$env:BATCH_SIZE="25"`

**If you get 500:**
- Check table schema matches JSON structure
- Verify foreign keys (hospital_id) reference existing hospitals

---

## ⚠️ PHASE E - Verification (USER ACTION REQUIRED)

### Run These SQL Queries in Supabase SQL Editor:

```sql
-- 1. Hospitals count (should be 51)
SELECT COUNT(*) as total_hospitals 
FROM hospitals 
WHERE is_active = true;
-- Expected: 51

-- 2. Doctors count (should be 405)
SELECT COUNT(*) as total_doctors 
FROM doctors;
-- Expected: 405

-- 3. Distinct cities (should be 31)
SELECT COUNT(DISTINCT city) as distinct_cities 
FROM hospitals 
WHERE is_active = true;
-- Expected: 31

-- 4. Check for orphan doctors (should be 0 or minimal)
SELECT COUNT(*) as orphan_doctors
FROM doctors d
LEFT JOIN hospitals h ON d.hospital_id = h.id
WHERE d.hospital_id IS NOT NULL AND h.id IS NULL;
-- Expected: 0 (or very few if some doctors don't have hospitals)

-- 5. Sample hospitals by city
SELECT city, COUNT(*) as hospital_count
FROM hospitals
WHERE is_active = true
GROUP BY city
ORDER BY hospital_count DESC
LIMIT 10;

-- 6. Sample doctors with hospital names
SELECT d.name, d.department, h.name as hospital_name, h.city
FROM doctors d
LEFT JOIN hospitals h ON d.hospital_id = h.id
WHERE d.hospital_id IS NOT NULL
LIMIT 5;

-- 7. Verify builder_plans exists (count may be 0)
SELECT COUNT(*) as builder_plans_count FROM builder_plans;
-- Expected: 0 (OK - user-generated)

-- 8. Verify cost_estimates exists (count may be 0)
SELECT COUNT(*) as cost_estimates_count FROM cost_estimates;
-- Expected: 0 (OK - user-generated)

-- 9. Verify tier column exists (if migration was run)
SELECT COUNT(*) as hospitals_with_tier
FROM hospitals
WHERE tier IS NOT NULL;
-- Expected: 0 initially (can be populated later)
```

---

## ✅ PHASE F - Final Checklist

### Production Readiness Status

| Check | Status | Action |
|-------|--------|--------|
| **Supabase URL correct** | ✅ **FIXED** | Function URLs updated in env.json |
| **All required tables exist** | ⚠️ **PENDING** | Run C1 check, apply C2 migrations |
| **Seeder ran successfully** | ⚠️ **PENDING** | Run D4 after setting env vars |
| **Hospitals count = 51** | ⚠️ **PENDING** | Verify after seeding (E1) |
| **Doctors count = 405** | ⚠️ **PENDING** | Verify after seeding (E1) |
| **Cities count = 31** | ⚠️ **PENDING** | Verify after seeding (E1) |
| **No orphan FKs** | ⚠️ **PENDING** | Verify after seeding (E1) |
| **builder_plans ready** | ✅ **READY** | Migration exists |
| **cost_estimates ready** | ⚠️ **PENDING** | Run migration if missing |

---

## 🎯 Execution Order

1. ✅ **PHASE A** - Complete (files verified)
2. ✅ **PHASE B** - Complete (URLs fixed)
3. ⚠️ **PHASE C** - **YOU RUN:** Check tables, apply migrations
4. ⚠️ **PHASE D** - **YOU RUN:** Set env vars, run seeder
5. ⚠️ **PHASE E** - **YOU RUN:** Verify counts
6. ✅ **PHASE F** - Complete (checklist ready)

---

## 📋 Quick Command Reference

```powershell
# 1. Navigate to backend
cd "C:\Users\AJINKYA\byonco-fastapi-backend"

# 2. Set environment variables
$env:SUPABASE_URL="https://thdpfewpikvunfyllmwj.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="YOUR_KEY_HERE"

# 3. Run seeder
python supabase_seed.py
```

---

**Status:** All code fixes complete. Ready for you to execute migrations and seeding.




