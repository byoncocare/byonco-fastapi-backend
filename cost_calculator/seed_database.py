import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from seed_data import (
    COUNTRIES_DATA, INSURERS_DATA, CANCER_TYPES_DATA,
    STAGES_DATA, HOSPITAL_TIERS_DATA, BASE_COSTS_DATA,
    ACCOMMODATION_COSTS_DATA
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_database():
    """Seed MongoDB with initial data"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("Starting database seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    await db.countries.delete_many({})
    await db.insurers.delete_many({})
    await db.cancer_types.delete_many({})
    await db.stages.delete_many({})
    await db.hospital_tiers.delete_many({})
    await db.base_costs.delete_many({})
    await db.accommodation_costs.delete_many({})
    
    # Insert countries
    print(f"Inserting {len(COUNTRIES_DATA)} countries...")
    await db.countries.insert_many(COUNTRIES_DATA)
    
    # Insert insurers
    print("Inserting insurers...")
    all_insurers = []
    for country_insurers in INSURERS_DATA.values():
        all_insurers.extend(country_insurers)
    await db.insurers.insert_many(all_insurers)
    print(f"Inserted {len(all_insurers)} insurers")
    
    # Insert cancer types
    print(f"Inserting {len(CANCER_TYPES_DATA)} cancer types...")
    await db.cancer_types.insert_many(CANCER_TYPES_DATA)
    
    # Insert stages
    print(f"Inserting {len(STAGES_DATA)} stages...")
    await db.stages.insert_many(STAGES_DATA)
    
    # Insert hospital tiers
    print(f"Inserting {len(HOSPITAL_TIERS_DATA)} hospital tiers...")
    await db.hospital_tiers.insert_many(HOSPITAL_TIERS_DATA)
    
    # Insert base costs
    print(f"Inserting {len(BASE_COSTS_DATA)} base costs...")
    await db.base_costs.insert_many(BASE_COSTS_DATA)
    
    # Insert accommodation costs
    print(f"Inserting {len(ACCOMMODATION_COSTS_DATA)} accommodation costs...")
    await db.accommodation_costs.insert_many(ACCOMMODATION_COSTS_DATA)
    
    print("\n✅ Database seeding completed successfully!")
    print(f"Total collections seeded: 7")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
