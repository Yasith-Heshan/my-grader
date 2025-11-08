"""
Script to clear all data from the database for testing
WARNING: This will delete ALL data!
"""
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

async def clear_database():
    """Clear all collections in the database"""
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    collections = ['teachers', 'students', 'assignments', 'test_cases', 'submissions', 'submission_items']
    
    print(f"\n⚠️  WARNING: About to delete all data from database '{settings.database_name}'")
    print(f"Collections to clear: {', '.join(collections)}")
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    print("\n🗑️  Clearing database...")
    for collection_name in collections:
        result = await db[collection_name].delete_many({})
        print(f"  ✅ Deleted {result.deleted_count} documents from '{collection_name}'")
    
    print("\n✅ Database cleared successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_database())
