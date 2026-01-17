# Quick Start: Seed Supabase Database

## Prerequisites

1. **Python** with `requests` installed:
   ```bash
   pip install requests
   ```

2. **Supabase Credentials**:
   - Project URL: `https://byonco-health.supabase.co` (or your actual project)
   - Service Role Key: Get from Supabase Dashboard → Settings → API

## Step 1: Export Data to JSON

```bash
cd C:\Users\AJINKYA\byonco-fastapi-backend
python export_seed_data.py
```

**Expected Output:**
```
Exporting seed data to JSON files...
  [OK] Exported 51 hospitals to ...\seed_exports\hospitals.json
  [OK] Saved hospital ID mapping to ...\seed_exports\hospital_id_mapping.json
  [OK] Exported 405 doctors to ...\seed_exports\doctors.json
  [OK] Exported 0 bed inventory records to ...\seed_exports\bed_inventory.json
  [OK] Exported 0 queue snapshots to ...\seed_exports\queue_snapshots.json
```

**Note:** The script generates UUIDs for hospitals and doctors, and properly maps `hospital_id` foreign keys.

## Step 2: Set Environment Variables

**PowerShell:**
```powershell
$env:SUPABASE_URL="https://byonco-health.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="your_service_role_key_here"
```

**Or use the helper script:**
```powershell
.\seed_supabase.ps1
```

## Step 3: Run Seeding

```bash
python supabase_seed.py
```

**Expected Output:**
```
[INFO] Supabase URL: https://byonco-health.supabase.co
[INFO] Seed dir: C:\Users\AJINKYA\byonco-fastapi-backend\seed_exports

[SEED] hospitals: 51 rows from ...\hospitals.json
[OK] hospitals batch 1/2 inserted (50/51)
[OK] hospitals batch 2/2 inserted (51/51)

[SEED] doctors: 405 rows from ...\doctors.json
[OK] doctors batch 1/9 inserted (50/405)
...
[OK] doctors batch 9/9 inserted (405/405)

✅ Done. Next: run verification SQL queries in Supabase SQL Editor.
```

## Step 4: Verify

Run these SQL queries in Supabase SQL Editor:

```sql
-- Count hospitals
SELECT COUNT(*) as total_hospitals FROM hospitals WHERE is_active = true;
-- Expected: 51

-- Count doctors
SELECT COUNT(*) as total_doctors FROM doctors;
-- Expected: 405 (43 regular + 362 specialists)

-- Count distinct cities
SELECT COUNT(DISTINCT city) as distinct_cities FROM hospitals WHERE is_active = true;
-- Expected: 31

-- Sample data
SELECT id, name, city, rating FROM hospitals LIMIT 5;
SELECT id, name, department, hospital_id FROM doctors LIMIT 5;
```

## Troubleshooting

### "Missing env vars"
- Make sure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Check for extra spaces in the values

### "Seed file not found"
- Run `python export_seed_data.py` first
- Check that `seed_exports/` folder exists

### "Insert failed" (400/409)
- **400**: Check JSON structure matches Supabase schema
- **409**: Data already exists (OK if using upsert)
- **401**: Check your service role key is correct

### "Connection timeout"
- Check internet connection
- Verify Supabase URL is correct
- Try reducing `BATCH_SIZE` in `supabase_seed.py`

## Notes

- The seeder uses **upsert mode** (safe to run multiple times)
- Data is inserted in **batches of 50** to avoid timeouts
- **0.25 second delay** between batches
- Missing files (bed_inventory, queue_snapshots) are skipped gracefully

## What Gets Seeded

- ✅ **51 hospitals** from `HOSPITALS` dict
- ✅ **405 doctors** (43 regular + 362 specialists from rare/common cancer specialists)
- ⏭️ **Bed inventory** - Empty (can be populated later)
- ⏭️ **Queue snapshots** - Empty (can be populated later)

