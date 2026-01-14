"""
Script to load sample Docker images for testing assignment creation
Run this after you have a teacher account created
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from beanie import PydanticObjectId
from database import connect_to_mongo
from models import CustomDockerImage, Teacher

async def load_sample_docker_images():
    """Load sample Docker images into the database"""
    
    # Connect to database
    await connect_to_mongo()
    
    # Get the first teacher (or create one if none exists)
    teacher = await Teacher.find_one()
    
    if not teacher:
        print("❌ No teacher found. Please create a teacher account first.")
        print("   Run: python -m scripts.seed_users")
        return
    
    teacher_id = str(teacher.id)
    print(f"✅ Using teacher: {teacher.email} (ID: {teacher_id})")
    
    # Load sample data
    json_file = Path(__file__).parent / "sample_docker_images.json"
    with open(json_file, 'r') as f:
        images_data = json.load(f)
    
    # Clear existing sample images (optional - comment out to keep existing)
    # await CustomDockerImage.find(CustomDockerImage.teacher_id == teacher_id).delete()
    # print("🗑️  Cleared existing Docker images")
    
    # Insert sample images
    created_images = []
    for img_data in images_data:
        # Replace teacher_id with actual teacher ID
        img_data['teacher_id'] = teacher_id
        
        # Add timestamps
        now = datetime.utcnow()
        img_data['created_at'] = now
        img_data['updated_at'] = now
        
        # Create image
        image = CustomDockerImage(**img_data)
        await image.insert()
        created_images.append(image)
        
        print(f"✅ Created: {image.name} ({image.status})")
    
    print(f"\n🎉 Successfully created {len(created_images)} sample Docker images!")
    print("\nYou can now:")
    print("1. Login as teacher")
    print("2. Create a new assignment")
    print("3. Select one of these Docker images from the dropdown")
    
    # Print summary
    print("\n📋 Sample Images Summary:")
    for img in created_images:
        packages = img.packages or []
        pip_cmds = img.pip_install_commands or ""
        pkg_info = f"{len(packages)} packages" if packages else "custom pip commands"
        print(f"   • {img.name}: {img.base_image} + {pkg_info}")

if __name__ == "__main__":
    asyncio.run(load_sample_docker_images())
