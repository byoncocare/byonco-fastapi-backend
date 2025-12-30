# Backend Modular Structure

This document describes the modular backend structure for ByOnco platform.

## Structure

The backend is now organized into separate modules, similar to the `cost_calculator` structure:

```
backend/
├── cost_calculator/      # Cost Calculator module
│   ├── api_routes.py
│   ├── models.py
│   ├── service.py
│   └── seed_database.py
├── hospitals/            # Find Hospitals module (NEW)
│   ├── api_routes.py
│   ├── models.py
│   ├── service.py
│   └── seed_data.py
├── rare_cancers/         # Rare Cancers module (NEW)
│   ├── api_routes.py
│   ├── models.py
│   ├── service.py
│   └── seed_data.py
└── server.py            # Main FastAPI application
```

## Hospitals Module

**Location:** `backend/hospitals/`

**Routes:**
- `GET /api/hospitals` - Get all hospitals (with optional city/cancer_type filters)
- `GET /api/hospitals/{hospital_id}` - Get specific hospital
- `GET /api/hospitals/{hospital_id}/doctors` - Get doctors for a hospital
- `GET /api/doctors` - Get all doctors (with optional city/specialty filters)
- `GET /api/doctors/{doctor_id}` - Get specific doctor

**Data Source:** Uses in-memory data from `backend/data_seed.py`

## Rare Cancers Module

**Location:** `backend/rare_cancers/`

**Routes:**
- `GET /api/rare-cancers` - Get all rare cancers (with optional category filter)
- `GET /api/rare-cancers/{cancer_name}` - Get detailed info about a specific rare cancer
- `GET /api/rare-cancers/category/{category}` - Get cancers by category (ultra-rare, very-rare, rare)
- `GET /api/rare-cancers/search/{query}` - Search rare cancers by name or type

**Data Source:** Uses in-memory data from `backend/data_seed.py`

## Cost Calculator Module

**Location:** `backend/cost_calculator/`

**Routes:**
- `GET /api/cost-calculator/countries`
- `GET /api/cost-calculator/insurers/{country_id}`
- `GET /api/cost-calculator/cancer-types`
- `GET /api/cost-calculator/stages`
- `GET /api/cost-calculator/hospital-tiers`
- `POST /api/cost-calculator/calculate-cost`

**Data Source:** Uses MongoDB (requires database connection)

## Running the Backend

1. **Activate virtual environment:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   ```

2. **Start the server:**
   ```powershell
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the server:**
   ```powershell
   python test_new_modules.py
   ```

## Testing

Run the test script to verify all modules are working:
```powershell
python test_new_modules.py
```

This will:
- Test imports for all modules
- Verify routers are created correctly
- List all available API routes
- Confirm server can start

## Notes

- All modules follow the same structure as `cost_calculator`
- Hospitals and Rare Cancers use in-memory data (no database required)
- Cost Calculator requires MongoDB connection
- All routes are prefixed with `/api/` for consistency
- The main `server.py` imports and includes all module routers


















