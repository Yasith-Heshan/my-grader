"""
Quick script to link a Docker image to an assignment
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def link_docker_to_assignment():
    """Link the Docker image to an assignment"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Get the Docker image we just created
        docker_image = await db.customdockerimages.find_one({"name": "matplotlib-image"})
        if not docker_image:
            print("❌ Docker image 'matplotlib-image' not found!")
            return
        
        print(f"🐳 Found Docker image: {docker_image['name']}")
        print(f"   ID: {docker_image['_id']}")
        print(f"   Packages: {', '.join(docker_image.get('packages', []))}")
        
        # List assignments
        print("\n📝 Available Assignments:")
        assignments = await db.assignments.find().to_list(length=100)
        for idx, assignment in enumerate(assignments, 1):
            has_docker = "✅" if assignment.get('custom_docker_image_id') else "⚪"
            print(f"{idx}. {has_docker} {assignment['title']} (ID: {assignment['_id']})")
        
        if not assignments:
            print("❌ No assignments found!")
            return
        
        # Auto-link to the first assignment (or you can make it interactive)
        print(f"\n🔗 Linking to all assignments...")
        
        for assignment in assignments:
            result = await db.assignments.update_one(
                {"_id": assignment["_id"]},
                {"$set": {"custom_docker_image_id": str(docker_image["_id"])}}
            )
            
            if result.modified_count > 0:
                print(f"   ✅ Linked to: {assignment['title']}")
            else:
                print(f"   ℹ️  Already linked or no change: {assignment['title']}")
        
        print(f"\n✅ Done! All assignments now use the matplotlib Docker image")
        print(f"   Restart the backend and try grading again!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(link_docker_to_assignment())
