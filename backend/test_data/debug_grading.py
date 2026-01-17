"""
Debug script to check what's happening during grading
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def debug_grading():
    """Debug the grading process"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Get the most recent submission
        submissions = await db.submissions.find().sort("created_at", -1).limit(5).to_list(length=5)
        
        if not submissions:
            print("❌ No submissions found!")
            return
        
        print("\n=== RECENT SUBMISSIONS ===\n")
        for sub in submissions:
            print(f"📝 Submission ID: {sub['_id']}")
            print(f"   Assignment ID: {sub.get('assignment_id')}")
            print(f"   Status: {sub.get('status')}")
            print(f"   Student: {sub.get('student_id')}")
            print(f"   Created: {sub.get('created_at')}")
            
            # Get assignment details
            assignment_id = sub.get('assignment_id')
            if assignment_id:
                try:
                    assignment = await db.assignments.find_one({"_id": ObjectId(assignment_id)})
                    if assignment:
                        print(f"   📚 Assignment: {assignment.get('title')}")
                        docker_id = assignment.get('custom_docker_image_id')
                        if docker_id:
                            print(f"   🐳 Has Docker Image ID: {docker_id}")
                            # Get Docker image
                            docker_img = await db.customdockerimages.find_one({"_id": ObjectId(docker_id)})
                            if docker_img:
                                print(f"      Image: {docker_img.get('full_image_name')}")
                                print(f"      Status: {docker_img.get('status')}")
                            else:
                                print(f"      ❌ Docker image not found!")
                        else:
                            print(f"   ⚠️  No custom Docker image")
                except Exception as e:
                    print(f"   ❌ Error fetching assignment: {e}")
            print()
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(debug_grading())
