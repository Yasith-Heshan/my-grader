"""
Script to update an existing assignment with a custom Docker image.
This will link an assignment to a Docker image so you can test the Docker image display feature.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "grader_system")


async def update_assignment_with_docker_image():
    """Update an assignment to use a custom Docker image"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # First, let's list available assignments
        print("\n=== Available Assignments ===")
        assignments = await db.assignments.find().to_list(length=100)
        for idx, assignment in enumerate(assignments, 1):
            print(f"{idx}. {assignment['title']} (ID: {assignment['_id']})")
        
        if not assignments:
            print("No assignments found!")
            return
        
        # List available Docker images
        print("\n=== Available Docker Images ===")
        docker_images = await db.customdockerimages.find({"status": "uploaded"}).to_list(length=100)
        for idx, image in enumerate(docker_images, 1):
            print(f"{idx}. {image['name']} - {image['full_image_name']}")
            print(f"   Status: {image['status']}, Packages: {', '.join(image.get('packages', []))}")
        
        if not docker_images:
            print("No uploaded Docker images found!")
            return
        
        # Get user input
        print("\n" + "="*50)
        assignment_idx = int(input("Enter assignment number to update: ")) - 1
        docker_idx = int(input("Enter Docker image number to use: ")) - 1
        
        if assignment_idx < 0 or assignment_idx >= len(assignments):
            print("Invalid assignment number!")
            return
            
        if docker_idx < 0 or docker_idx >= len(docker_images):
            print("Invalid Docker image number!")
            return
        
        assignment = assignments[assignment_idx]
        docker_image = docker_images[docker_idx]
        
        # Update the assignment
        result = await db.assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": {"custom_docker_image_id": str(docker_image["_id"])}}
        )
        
        if result.modified_count > 0:
            print(f"\n✅ Successfully updated assignment '{assignment['title']}'")
            print(f"   Now using Docker image: {docker_image['name']}")
            print(f"   Docker Hub tag: {docker_image['full_image_name']}")
        else:
            print(f"\n⚠️ No changes made to assignment '{assignment['title']}'")
            
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()


async def remove_docker_image_from_assignment():
    """Remove Docker image from an assignment (revert to default)"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # List assignments with Docker images
        print("\n=== Assignments with Custom Docker Images ===")
        assignments = await db.assignments.find({"custom_docker_image_id": {"$exists": True, "$ne": None}}).to_list(length=100)
        
        if not assignments:
            print("No assignments with custom Docker images found!")
            return
        
        for idx, assignment in enumerate(assignments, 1):
            print(f"{idx}. {assignment['title']} (Docker Image ID: {assignment.get('custom_docker_image_id')})")
        
        # Get user input
        print("\n" + "="*50)
        assignment_idx = int(input("Enter assignment number to remove Docker image from: ")) - 1
        
        if assignment_idx < 0 or assignment_idx >= len(assignments):
            print("Invalid assignment number!")
            return
        
        assignment = assignments[assignment_idx]
        
        # Remove the Docker image
        result = await db.assignments.update_one(
            {"_id": assignment["_id"]},
            {"$unset": {"custom_docker_image_id": ""}}
        )
        
        if result.modified_count > 0:
            print(f"\n✅ Successfully removed Docker image from '{assignment['title']}'")
            print(f"   Assignment will now use the default Python environment")
        else:
            print(f"\n⚠️ No changes made to assignment '{assignment['title']}'")
            
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()


async def main():
    """Main menu"""
    print("\n" + "="*50)
    print("Assignment Docker Image Manager")
    print("="*50)
    print("1. Add Docker image to assignment")
    print("2. Remove Docker image from assignment")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        await update_assignment_with_docker_image()
    elif choice == "2":
        await remove_docker_image_from_assignment()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    asyncio.run(main())
