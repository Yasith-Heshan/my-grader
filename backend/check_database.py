"""
Check MongoDB database contents
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

async def check_database():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    print(f"\nDatabase: {settings.database_name}")
    print("="*60)
    
    # List all collections
    collections = await db.list_collection_names()
    print(f"\nCollections found: {collections}")
    
    # Check each collection
    for collection_name in collections:
        collection = db[collection_name]
        count = await collection.count_documents({})
        print(f"\n{collection_name}: {count} documents")
        
        if count > 0:
            # Show first few documents
            cursor = collection.find({}).limit(3)
            docs = await cursor.to_list(length=3)
            for i, doc in enumerate(docs, 1):
                print(f"\n  Document {i}:")
                for key, value in doc.items():
                    if key == '_id':
                        print(f"    {key}: {value}")
                    elif isinstance(value, str) and len(value) > 100:
                        print(f"    {key}: {value[:100]}...")
                    else:
                        print(f"    {key}: {value}")
    
    client.close()
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(check_database())
