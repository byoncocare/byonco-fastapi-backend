# Supabase Seeding Guide

This guide explains how to seed your Supabase database with data from the backend seed files.

## Prerequisites

1. **Supabase Project**: You need a valid Supabase project URL and service role key
2. **Python Environment**: Ensure you have `requests` installed:
   ```bash
   pip install requests
   ```

## Step 1: Export Data to JSON

First, convert your Python seed data into JSON files:

```bash
cd C:\Users\AJINKYA\byonco-fastapi-backend
python export_seed_data.py
```

This will create JSON files in `seed_exports/`:
- `hospitals.json` - All hospitals (51 entries)
- `doctors.json` - All doctors + specialists (200+ entries)
- `bed_inventory.json` - Empty (can be populated later)
- `queue_snapshots.json` - Empty (can be populated later)

## Step 2: Set Environment Variables

**Option A: PowerShell (Windows)**
```powershell
cd C:\Users\AJINKYA\byonco-fastapi-backend

$env:SUPABASE_URL="https://byonco-health.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="your_service_role_key_here"
$env:SEED_DIR="C:\Users\AJINKYA\byonco-fastapi-backend\seed_exports"

python supabase_seed.py
```

**Option B: Command Prompt (Windows)**
```cmd
cd C:\Users\AJINKYA\byonco-fastapi-backend

set SUPABASE_URL=https://byonco-health.supabase.co
set SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
set SEED_DIR=C:\Users\AJINKYA\byonco-fastapi-backend\seed_exports

python supabase_seed.py
```

**Option C: Create `.env` file (Recommended)**
Create a `.env` file in the backend folder:
```
SUPABASE_URL=https://byonco-health.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SEED_DIR=C:\Users\AJINKYA\byonco-fastapi-backend\seed_exports
```

Then use `python-dotenv` to load it:
```python
# Add to top of supabase_seed.py
from dotenv import load_dotenv
load_dotenv()
```

## Step 3: Run the Seeder

```bash
python supabase_seed.py
```

The script will:
- Validate environment variables
- Load JSON files from `seed_exports/`
- Insert data in batches (50 rows per batch)
- Use upsert mode (safe to run multiple times)
- Show progress for each table

## Step 4: Verify Data

Run these SQL queries in Supabase SQL Editor:

```sql
-- Count hospitals
SELECT COUNT(*) as total_hospitals FROM hospitals WHERE is_active = true;

-- Count doctors
SELECT COUNT(*) as total_doctors FROM doctors;

-- Count distinct cities
SELECT COUNT(DISTINCT city) as distinct_cities FROM hospitals WHERE is_active = true;

-- Sample hospitals
SELECT id, name, city, rating, tier FROM hospitals LIMIT 10;

-- Sample doctors
SELECT id, name, department, hospital_id FROM doctors LIMIT 10;
```

## Expected Results

After seeding, you should see:
- **51 hospitals** in the `hospitals` table
- **200+ doctors** in the `doctors` table (43 regular + 157+ specialists)
- **31 distinct cities** in the hospitals table

## Troubleshooting

### Error: "Missing env vars"
- Make sure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Check that the values don't have extra spaces

### Error: "Seed file not found"
- Run `export_seed_data.py` first to generate JSON files
- Check that `seed_exports/` folder exists and contains the JSON files

### Error: "Insert failed" (400/409)
- **400 Bad Request**: Check that JSON structure matches Supabase schema
- **409 Conflict**: Data already exists (this is OK if using upsert)
- **401 Unauthorized**: Check your service role key

### Error: "Connection timeout"
- Check your internet connection
- Verify Supabase URL is correct
- Try reducing `BATCH_SIZE` in the script

## Adding Tier Column (Optional)

If you want to use the `tier` field from seed data, add this migration:

```sql
-- Add tier column to hospitals table
ALTER TABLE public.hospitals 
ADD COLUMN IF NOT EXISTS tier TEXT CHECK(tier IN ('Tier 1', 'Tier 2', 'Tier 3'));

CREATE INDEX IF NOT EXISTS idx_hospitals_tier ON public.hospitals(tier);

-- Top hospitals = WHERE tier = 'Tier 1'
```

Then re-run the export and seed:
```bash
python export_seed_data.py
python supabase_seed.py
```

## Reseeding (Clean Start)

If you need to start fresh:

1. **Truncate tables** (in Supabase SQL Editor):
```sql
TRUNCATE TABLE hospitals CASCADE;
TRUNCATE TABLE doctors CASCADE;
-- Note: CASCADE will also delete related records
```

2. **Re-run seeding**:
```bash
python supabase_seed.py
```

## Notes

- The seeder uses **upsert mode** by default (safe to run multiple times)
- Data is inserted in **batches of 50** to avoid timeouts
- There's a **0.25 second delay** between batches to be gentle on the API
- The script will **skip missing files** (bed_inventory, queue_snapshots can be empty)




