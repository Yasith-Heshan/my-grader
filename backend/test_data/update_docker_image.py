"""
Update Docker image to use full Python with matplotlib support
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def update_image():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Note: python:3.11 still doesn't have matplotlib pre-installed
        # We're using it as a placeholder. In production, you'd need:
        # 1. A custom image with matplotlib pre-installed, OR
        # 2. Install it at runtime (which the executor doesn't currently do)
        
        result = await db.customdockerimages.update_one(
            {'name': 'matplotlib-image'},
            {'$set': {
                'full_image_name': 'python:3.11',
                'base_image': 'python:3.11'
            }}
        )
        
        print(f"✅ Updated {result.modified_count} Docker image(s)")
        print(f"\n⚠️  IMPORTANT: python:3.11 doesn't have matplotlib pre-installed!")
        print(f"   The grading will still fail unless:")
        print(f"   1. You create a custom Docker image with matplotlib, OR")
        print(f"   2. Use an existing image like 'continuumio/miniconda3' that has it")
        
        # Let's update to use a better base image
        result2 = await db.customdockerimages.update_one(
            {'name': 'matplotlib-image'},
            {'$set': {
                'full_image_name': 'continuumio/miniconda3:latest',
                'base_image': 'continuumio/miniconda3:latest',
                'description': 'Miniconda environment with matplotlib, numpy, pandas'
            }}
        )
        
        if result2.modified_count > 0:
            print(f"\n✅ Updated to use continuumio/miniconda3 (has conda & scientific packages)")
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(update_image())
