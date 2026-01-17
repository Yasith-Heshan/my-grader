"""
Check if an assignment has a custom Docker image linked
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def check_assignment_docker():
    """Check assignment Docker image configuration"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Get all assignments
        print("\n=== CHECKING ASSIGNMENTS ===\n")
        assignments = await db.assignments.find().to_list(length=100)
        
        for assignment in assignments:
            print(f"📝 Assignment: {assignment['title']}")
            print(f"   ID: {assignment['_id']}")
            
            docker_id = assignment.get('custom_docker_image_id')
            if docker_id:
                print(f"   ✅ Has custom_docker_image_id: {docker_id}")
                
                # Try to fetch the Docker image
                try:
                    docker_image = await db.customdockerimages.find_one({"_id": ObjectId(docker_id)})
                    if docker_image:
                        print(f"   🐳 Docker Image Found:")
                        print(f"      Name: {docker_image['name']}")
                        print(f"      Full Image: {docker_image['full_image_name']}")
                        print(f"      Status: {docker_image['status']}")
                        print(f"      Packages: {', '.join(docker_image.get('packages', []))}")
                    else:
                        print(f"   ❌ Docker image with ID {docker_id} NOT FOUND in database!")
                except Exception as e:
                    print(f"   ❌ Error fetching Docker image: {e}")
            else:
                print(f"   ⚠️  No custom_docker_image_id (using default Python)")
            
            print()
        
        # Get all Docker images
        print("\n=== ALL DOCKER IMAGES ===\n")
        images = await db.customdockerimages.find().to_list(length=100)
        
        for img in images:
            print(f"🐳 {img['name']}")
            print(f"   ID: {img['_id']}")
            print(f"   Full Image: {img['full_image_name']}")
            print(f"   Status: {img['status']}")
            print(f"   Packages: {', '.join(img.get('packages', []))}")
            print()
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(check_assignment_docker())
