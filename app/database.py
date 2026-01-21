"""
Database connection setup
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URL, DB_NAME

# MongoDB Connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def get_db():
    """Get database instance"""
    return db

def get_client():
    """Get MongoDB client instance"""
    return client

