"""
Create a sample custom Docker image in the database for testing
This simulates what would happen when a teacher uploads a Docker image
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def create_sample_docker_image():
    """Create a sample Docker image with matplotlib"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # First, get a teacher ID
        teachers = await db.teachers.find().to_list(length=1)
        if not teachers:
            print("❌ No teachers found! Create a teacher first.")
            return
        
        teacher = teachers[0]
        teacher_id = str(teacher['_id'])
        
        # Create a sample Docker image
        docker_image = {
            "name": "matplotlib-image",
            "description": "Python environment with matplotlib, numpy, and pandas",
            "teacher_id": teacher_id,
            "teacher_name": teacher.get('name', 'Teacher'),
            "docker_hub_username": "testuser",
            "full_image_name": "python:3.11-slim",  # For testing, use standard Python image (has matplotlib via pip)
            "base_image": "python:3.11-slim",
            "packages": ["matplotlib", "numpy", "pandas"],
            "status": "uploaded",  # Mark as uploaded
            "size_mb": 450.5,
            "build_time_seconds": 120.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "uploaded_at": datetime.utcnow(),
            "usage_count": 0
        }
        
        result = await db.customdockerimages.insert_one(docker_image)
        image_id = str(result.inserted_id)
        
        print(f"✅ Created Docker image:")
        print(f"   ID: {image_id}")
        print(f"   Name: {docker_image['name']}")
        print(f"   Full Image: {docker_image['full_image_name']}")
        print(f"   Packages: {', '.join(docker_image['packages'])}")
        print(f"\n📝 Now link this to an assignment:")
        print(f"   python update_assignment_docker_image.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(create_sample_docker_image())
