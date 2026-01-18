"""
Script to create or update admin user with specified credentials
Run this script to ensure admin account exists with correct password
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from motor.motor_asyncio import AsyncIOMotorClient

# Add auth module to path
auth_path = Path(__file__).parent.parent / "auth"
sys.path.insert(0, str(auth_path))

from auth.service import AuthService
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

ADMIN_EMAIL = "imajinkyajadhav@gmail.com"
ADMIN_PASSWORD = ",t$+.VNq6Tmk6+:"
ADMIN_NAME = "Admin User"
ADMIN_PHONE = "+919999999999"  # Placeholder phone

async def create_admin_user():
    """Create or update admin user"""
    # Get MongoDB connection string (backend uses MONGO_URL and DB_NAME)
    mongo_url = os.getenv("MONGO_URL", "")
    db_name = os.getenv("DB_NAME", "")
    
    # Fallback: Try MONGODB_URI if MONGO_URL not found
    if not mongo_url:
        mongodb_uri = os.getenv("MONGODB_URI", "")
        if mongodb_uri:
            mongo_url = mongodb_uri
            if not db_name:
                # Extract db name from URI if not set separately
                db_name = mongodb_uri.split("/")[-1].split("?")[0]
    
    if not mongo_url:
        print("❌ MONGO_URL or MONGODB_URI not found in environment variables")
        print("💡 Please set MONGO_URL and DB_NAME in your .env file")
        return
    
    if not db_name:
        db_name = "byonco"  # Default database name
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    auth_service = AuthService(db)
    
    try:
        # Check if user exists
        existing_user = await auth_service.users_collection.find_one({"email": ADMIN_EMAIL.lower()})
        
        if existing_user:
            # Update password if user exists
            print(f"✅ User {ADMIN_EMAIL} already exists. Updating password...")
            new_password_hash = auth_service.hash_password(ADMIN_PASSWORD)
            await auth_service.users_collection.update_one(
                {"email": ADMIN_EMAIL.lower()},
                {"$set": {
                    "password_hash": new_password_hash,
                    "full_name": ADMIN_NAME,
                    "phone": ADMIN_PHONE,
                    "is_verified": True,
                    "profile_completed": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            print(f"✅ Admin user password updated successfully!")
        else:
            # Create new user
            print(f"📝 Creating admin user {ADMIN_EMAIL}...")
            user_doc = await auth_service.register_user(
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
                full_name=ADMIN_NAME,
                phone=ADMIN_PHONE
            )
            
            # Mark as verified and profile completed
            await auth_service.users_collection.update_one(
                {"email": ADMIN_EMAIL.lower()},
                {"$set": {
                    "is_verified": True,
                    "profile_completed": True
                }}
            )
            print(f"✅ Admin user created successfully!")
        
        print(f"\n📋 Admin Account Details:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   Status: Active")
        
    except Exception as e:
        print(f"❌ Error creating/updating admin user: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
