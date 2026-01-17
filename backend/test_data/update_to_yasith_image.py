"""
Update all assignments to use the yasithheshan custom Docker image
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def update_to_custom_image():
    """Update assignments to use the yasithheshan custom image"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Find the yasithheshan custom image
        custom_image = await db.customdockerimages.find_one({
            "full_image_name": {"$regex": "yasithheshan/grader-python"}
        })
        
        if not custom_image:
            print("❌ yasithheshan custom Docker image not found!")
            return
        
        print(f"✅ Found custom image:")
        print(f"   ID: {custom_image['_id']}")
        print(f"   Name: {custom_image['name']}")
        print(f"   Full Image: {custom_image['full_image_name']}")
        print(f"   Packages: {', '.join(custom_image.get('packages', []))}")
        
        # Update all assignments
        print(f"\n🔄 Updating all assignments...")
        result = await db.assignments.update_many(
            {},  # Update all assignments
            {"$set": {"custom_docker_image_id": str(custom_image["_id"])}}
        )
        
        print(f"\n✅ Updated {result.modified_count} assignment(s)")
        print(f"   Matched {result.matched_count} assignment(s)")
        
        # Show updated assignments
        print(f"\n📝 Updated Assignments:")
        assignments = await db.assignments.find().to_list(length=100)
        for assignment in assignments:
            print(f"   • {assignment['title']} → {assignment.get('custom_docker_image_id')}")
        
        print(f"\n✅ Done! Restart backend and regrade submissions.")
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(update_to_custom_image())
