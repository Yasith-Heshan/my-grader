"""
Quick script to check what assignments and Docker images exist in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def check_database():
    """Check database contents"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Check assignments
        print("\n=== ASSIGNMENTS ===")
        assignments = await db.assignments.find().to_list(length=100)
        print(f"Total assignments: {len(assignments)}\n")
        
        for assignment in assignments:
            docker_id = assignment.get('custom_docker_image_id', 'None')
            print(f"• {assignment['title']}")
            print(f"  ID: {assignment['_id']}")
            print(f"  Docker Image ID: {docker_id}")
            print(f"  Created: {assignment.get('created_at', 'N/A')}")
            print()
        
        # Check Docker images
        print("\n=== CUSTOM DOCKER IMAGES ===")
        docker_images = await db.customdockerimages.find().to_list(length=100)
        print(f"Total Docker images: {len(docker_images)}\n")
        
        for image in docker_images:
            print(f"• {image['name']}")
            print(f"  ID: {image['_id']}")
            print(f"  Full name: {image['full_image_name']}")
            print(f"  Status: {image['status']}")
            print(f"  Packages: {', '.join(image.get('packages', []))}")
            print(f"  Teacher ID: {image.get('teacher_id', 'N/A')}")
            print()
        
        # Check if any assignments use Docker images
        print("\n=== ASSIGNMENTS WITH DOCKER IMAGES ===")
        assignments_with_docker = await db.assignments.find(
            {"custom_docker_image_id": {"$exists": True, "$ne": None}}
        ).to_list(length=100)
        
        if assignments_with_docker:
            for assignment in assignments_with_docker:
                print(f"• {assignment['title']} → Docker ID: {assignment['custom_docker_image_id']}")
        else:
            print("No assignments are currently using custom Docker images.")
            print("\n💡 To link an assignment to a Docker image:")
            print("   Run: python update_assignment_docker_image.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(check_database())
