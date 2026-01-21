"""
Production-ready Supabase seeding script.
Reads JSON files from seed_exports/ and inserts into Supabase via REST API.
"""
import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

# -----------------------------
# CONFIG
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

# IMPORTANT: point these to your actual seed files.
SEED_DIR = os.getenv("SEED_DIR", os.path.join(os.path.dirname(__file__), "seed_exports"))

TABLE_FILES = {
    "hospitals": "hospitals.json",
    "doctors": "doctors.json",
    "bed_inventory": "bed_inventory.json",
    "queue_snapshots": "queue_snapshots.json",
    # Optional:
    # "cancer_types": "cancer_types.json",
}

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))  # Reduced for safety
SLEEP_BETWEEN_BATCHES_SEC = float(os.getenv("SLEEP_SEC", "0.25"))

# -----------------------------
# HELPERS
# -----------------------------
def require_env():
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

def load_json_list(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Seed file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        return data["data"]
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}, got {type(data)}")
    return data

def postgrest_insert(table: str, rows: List[Dict[str, Any]], upsert: bool = True) -> Tuple[int, str]:
    """
    Inserts rows into Supabase via PostgREST.
    Uses upsert style if upsert=True (recommended for idempotency).
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    
    # Use upsert to handle duplicates gracefully
    if upsert:
        headers["Prefer"] = "resolution=merge-duplicates,return=minimal"

    try:
        resp = requests.post(url, headers=headers, json=rows, timeout=60)
        return resp.status_code, resp.text
    except requests.exceptions.RequestException as e:
        return 0, str(e)

def truncate_table(table: str):
    """
    Use SQL Editor for truncation if you prefer.
    But if you want programmatic truncation, call an RPC or use SQL manually.
    Here we just warn.
    """
    print(f"[INFO] If you need a clean reseed, TRUNCATE {table} from SQL Editor.")

def seed_table(table: str, filename: str, upsert: bool = True):
    path = os.path.join(SEED_DIR, filename)
    
    if not os.path.exists(path):
        print(f"[SKIP] {table}: File not found at {path}. Skipping.")
        return
    
    rows = load_json_list(path)
    total = len(rows)
    print(f"\n[SEED] {table}: {total} rows from {path}")

    if total == 0:
        print(f"[WARN] {table} seed file empty. Skipping.")
        return

    batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(batches):
        start = i * BATCH_SIZE
        end = min(start + BATCH_SIZE, total)
        chunk = rows[start:end]

        status, text = postgrest_insert(table, chunk, upsert=upsert)
        if status not in (200, 201, 204):
            print(f"[ERROR] Insert failed for {table} batch {i+1}/{batches}")
            print(f"Status: {status}\nResponse: {text}")
            # Don't exit on first error - continue with other tables
            print(f"[WARN] Continuing with other tables...")
            return

        print(f"[OK] {table} batch {i+1}/{batches} inserted ({end}/{total})")
        time.sleep(SLEEP_BETWEEN_BATCHES_SEC)

def main():
    require_env()

    # Log URL without exposing full value (security)
    if SUPABASE_URL:
        url_display = SUPABASE_URL[:20] + "..." if len(SUPABASE_URL) > 20 else SUPABASE_URL
        print(f"[INFO] Supabase URL configured: {url_display}")
    else:
        print("[INFO] Supabase URL: Not set")
    print("[INFO] Seed dir:", SEED_DIR)
    print("[INFO] Batch size:", BATCH_SIZE)
    print()

    for table, file in TABLE_FILES.items():
        try:
            seed_table(table, file, upsert=True)
        except Exception as e:
            print(f"[ERROR] Failed to seed {table}: {e}")
            continue

    print("\n✅ Done. Next: run verification SQL queries in Supabase SQL Editor.")
    print("\nVerification queries:")
    print("  SELECT COUNT(*) FROM hospitals;")
    print("  SELECT COUNT(*) FROM doctors;")
    print("  SELECT COUNT(DISTINCT city) FROM hospitals;")

if __name__ == "__main__":
    main()




