# ByOnco FastAPI Backend

Production-grade FastAPI backend for the ByOnco AI-Powered Cancer Care Platform.

## Project Structure

```
byonco-fastapi-backend/
├── app/                          # Main application package (ALL runtime code)
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Environment/config management
│   ├── database.py               # MongoDB connection setup
│   ├── core/                     # Core utilities & shared code
│   │   ├── __init__.py
│   │   ├── models.py             # Shared Pydantic models
│   │   └── email_service.py      # Email service
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── v1/                   # API versioning
│   │   │   ├── __init__.py
│   │   │   └── router.py         # Main API router
│   │   └── modules/              # Feature modules
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
│       └── seed_data.py          # Main seed data
├── scripts/                      # Operational scripts
│   ├── admin/                    # Admin utilities
│   │   ├── create_admin_user.py
│   │   └── register_whatsapp_number.py
│   ├── seeding/                  # Database seeding scripts
│   │   ├── export_seed_data.py
│   │   ├── seed_database.py
│   │   └── supabase_seed.py
│   ├── testing/                  # Test scripts
│   │   ├── test_endpoints.py
│   │   ├── test_new_modules.py
│   │   └── test_server.py
│   ├── verification/             # Verification scripts
│   │   └── verify_routes.py
│   └── run.ps1                   # Windows PowerShell run script
├── docs/                         # Documentation
│   ├── deployment/               # Deployment guides
│   ├── operations/              # Operational guides
│   └── guides/                  # General guides
├── archive/                      # Legacy files (preserved)
├── requirements.txt
├── Makefile                      # Unix commands
└── server.py                     # Compatibility shim (imports from app.main)

```

## How to Run Locally

### Prerequisites

- Python 3.8+
- MongoDB (local or remote)
- Environment variables configured (see `.env.example`)

### Quick Start

**Windows (PowerShell):**
```powershell
# Install dependencies
.\scripts\run.ps1 install

# Run development server
.\scripts\run.ps1 run

# Run tests
.\scripts\run.ps1 test

# Seed database
.\scripts\run.ps1 seed
```

**Unix/Mac (Make):**
```bash
# Install dependencies
make install

# Run development server
make run

# Run tests
make test

# Seed database
make seed
```

**Direct Python:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the compatibility shim
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Required environment variables (set in `.env` or Render/Vercel):

- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `RAZORPAY_KEY_ID` - Razorpay key ID (for payments)
- `RAZORPAY_KEY_SECRET` - Razorpay key secret (for payments)
- `RAZORPAY_WEBHOOK_SECRET` - Razorpay webhook secret
- `JWT_SECRET_KEY` or `SECRET_KEY` - JWT signing secret
- `SMTP_USERNAME`, `SMTP_PASSWORD` - Email service (optional)
- `OPENAI_API_KEY` - OpenAI API key (for AI features, optional)
- `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERIFY_TOKEN` - WhatsApp integration (optional)

See `docs/operations/RENDER_ENV_VARS.md` for complete list.

## API Endpoints

All API endpoints are prefixed with `/api`:

- `/api/` - API root
- `/api/hospitals` - Hospital search and details
- `/api/cost-calculator` - Treatment cost calculator
- `/api/auth` - Authentication endpoints
- `/api/payments` - Payment processing
- `/api/second-opinion` - Second opinion requests
- `/api/journey-builder` - AI journey builder
- `/api/whatsapp` - WhatsApp webhook

See `docs/guides/README_MODULES.md` for detailed API documentation.

## Development

### Running Tests

```bash
# All tests
make test
# or
.\scripts\run.ps1 test

# Individual test files
python scripts/testing/test_server.py
python scripts/testing/test_endpoints.py
python scripts/testing/test_new_modules.py
```

### Verifying Routes

```bash
make verify
# or
.\scripts\run.ps1 verify
```

### Creating Admin User

```bash
make admin
# or
.\scripts\run.ps1 admin
```

**Note:** Requires `ADMIN_PASSWORD` environment variable to be set.

## Deployment

### Render Deployment

The backend is configured for Render deployment. See:
- `docs/deployment/RENDER_DEPLOYMENT_CONFIG.md`
- `docs/deployment/RENDER_ENV_VARS.md`

### Entry Point

The application entry point is `app.main:app` (or `server:app` for backward compatibility).

Render build command:
```bash
pip install -r requirements.txt
```

Render start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Backward Compatibility

This refactored structure maintains full backward compatibility:

- `server.py` is a compatibility shim that imports from `app.main`
- `data_seed.py` is a compatibility shim that imports from `app.data.seed_data`
- `email_service.py` is a compatibility shim that imports from `app.core.email_service`
- All API routes remain identical (`/api/*`, `/api/hospitals/*`, etc.)
- Environment variables unchanged
- Database connection unchanged

## Module Organization

Each feature module in `app/api/modules/` follows a consistent structure:

```
module_name/
├── __init__.py
├── api_routes.py      # FastAPI routes
├── models.py          # Pydantic models
├── service.py         # Business logic
└── seed_data.py       # Module-specific seed data (if needed)
```

## Security

- All secrets are read from environment variables only
- No hardcoded credentials in code
- JWT secret key must be set via `JWT_SECRET_KEY` or `SECRET_KEY`
- Admin password must be set via `ADMIN_PASSWORD` environment variable

See `docs/operations/SECURITY_FIX_COMPLETE.md` for security details.

## License

Proprietary - ByOnco by PraesidioCare Private Limited

