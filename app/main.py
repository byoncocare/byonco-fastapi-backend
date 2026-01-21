"""
FastAPI application entry point
This is the main application file that creates and configures the FastAPI app.
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration and database
from app.config import CORS_ORIGINS
from app.database import db, client

# Import main API router
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ======================================
# FastAPI App Creation
# ======================================
app = FastAPI(
    title="ByOnco API",
    description="AI-Powered Cancer Care Platform API",
    version="1.0.0",
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins to fix CORS issues in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================
# Root Route
# ======================================
@app.get("/")
async def root():
    # Get all registered routes for debugging
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    
    return {
        "message": "ByOnco API Server",
        "version": "1.0.0",
        "endpoints": {
            "api_root": "/api",
            "hospitals": "/api/hospitals",
            "cancer_types": "/api/cancer-types",
            "cities": "/api/cities",
            "doctors": "/api/doctors"
        },
        "registered_routes": routes[:20]  # Show first 20 routes for debugging
    }

# ======================================
# Register Main API Router
# ======================================
app.include_router(api_router)

# ======================================
# Cost Calculator Routes
# ======================================
# Note: cost_calculator uses a special import pattern with sys.path manipulation
# We maintain this for backward compatibility
cost_calculator_path = Path(__file__).parent.parent / "app" / "api" / "modules" / "cost_calculator"
if str(cost_calculator_path) not in sys.path:
    sys.path.insert(0, str(cost_calculator_path))

try:
    from api_routes import create_api_router as create_cost_calculator_router
    cost_calculator_router = create_cost_calculator_router(db)
    app.include_router(cost_calculator_router)
    logger.info("✅ Included cost_calculator_router")
except Exception as e:
    logger.error(f"❌ Failed to include cost_calculator_router: {e}")

# ======================================
# Hospitals Routes (Modular)
# ======================================
try:
    from app.api.modules.hospitals.api_routes import create_api_router as create_hospitals_router
    hospitals_router = create_hospitals_router()
    app.include_router(hospitals_router)
    logger.info("✅ Included hospitals_router")
except Exception as e:
    logger.error(f"❌ Failed to include hospitals_router: {e}")

# ======================================
# Rare Cancers Routes (Modular)
# ======================================
try:
    from app.api.modules.rare_cancers.api_routes import create_api_router as create_rare_cancers_router
    rare_cancers_router = create_rare_cancers_router()
    app.include_router(rare_cancers_router)
    logger.info("✅ Included rare_cancers_router")
except Exception as e:
    logger.error(f"❌ Failed to include rare_cancers_router: {e}")

# ======================================
# Authentication Routes
# ======================================
try:
    from app.api.modules.auth.api_routes import create_api_router as create_auth_router
    auth_router = create_auth_router(db)
    app.include_router(auth_router)
    logger.info("✅ Included auth_router")
except Exception as e:
    logger.error(f"❌ Failed to include auth_router: {e}")

# ======================================
# Payment Routes
# ======================================
try:
    from app.api.modules.payments.api_routes import create_api_router as create_payments_router
    payments_router, razorpay_router = create_payments_router(db)
    app.include_router(payments_router)
    app.include_router(razorpay_router)
    logger.info("✅ Included payments_router and razorpay_router")
except Exception as e:
    logger.error(f"❌ Failed to include payments_router: {e}")

# ======================================
# Get Started Routes
# ======================================
try:
    from app.api.modules.get_started.api_routes import create_api_router as create_get_started_router
    get_started_router = create_get_started_router(db)
    app.include_router(get_started_router)
    logger.info("✅ Included get_started_router")
except Exception as e:
    logger.error(f"❌ Failed to include get_started_router: {e}")

# ======================================
# Waitlist Routes
# ======================================
try:
    from app.api.modules.waitlist.api_routes import create_api_router as create_waitlist_router
    waitlist_router = create_waitlist_router(db)
    app.include_router(waitlist_router)
    logger.info("✅ Included waitlist_router")
except Exception as e:
    logger.error(f"❌ Failed to include waitlist_router: {e}")

# ======================================
# Journey Builder Routes
# ======================================
try:
    from app.api.modules.journey_builder.api_routes import create_api_router as create_journey_builder_router
    journey_builder_router = create_journey_builder_router()
    app.include_router(journey_builder_router)
    logger.info("✅ Included journey_builder_router")
except Exception as e:
    logger.error(f"❌ Failed to include journey_builder_router: {e}")

# ======================================
# Second Opinion AI Routes
# ======================================
try:
    from app.api.modules.second_opinion.api_routes import create_api_router as create_second_opinion_ai_router
    second_opinion_ai_router = create_second_opinion_ai_router()
    app.include_router(second_opinion_ai_router)
    logger.info("✅ Included second_opinion_ai_router")
except Exception as e:
    logger.error(f"❌ Failed to include second_opinion_ai_router: {e}")

# ======================================
# WhatsApp Routes
# ======================================
try:
    from app.api.modules.whatsapp.api_routes import create_api_router as create_whatsapp_router
    whatsapp_router = create_whatsapp_router()
    app.include_router(
        whatsapp_router,
        prefix="/api/whatsapp",
        tags=["WhatsApp"]
    )
    logger.info("✅ Included whatsapp_router")
except Exception as e:
    logger.error(f"❌ Failed to include whatsapp_router: {e}")

# ======================================
# Startup Handler - Log Razorpay env status
# ======================================
@app.on_event("startup")
async def startup_log_razorpay():
    """Log Razorpay environment variable status at startup (no secrets)."""
    raw_key_id = os.getenv("RAZORPAY_KEY_ID", "") or ""
    key_id = raw_key_id.strip()
    key_secret_present = bool(os.getenv("RAZORPAY_KEY_SECRET", "").strip())

    key_id_present = bool(key_id)
    logger.info(f"Razorpay env present? id={key_id_present} secret={key_secret_present}")

    if key_id_present and key_secret_present:
        mode = "UNKNOWN"
        if key_id.startswith("rzp_live_"):
            mode = "LIVE"
        elif key_id.startswith("rzp_test_"):
            mode = "TEST"

        safe_prefix = key_id[:8] if len(key_id) >= 8 else key_id
        logger.info(
            f"✅ Razorpay environment variables configured – mode={mode}, key_prefix={safe_prefix}"
        )
    else:
        logger.warning("⚠️ Razorpay environment variables missing - payment features will not work")

# ======================================
# Shutdown Handler
# ======================================
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
