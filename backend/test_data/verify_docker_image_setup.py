"""
Quick verification script to check Docker image selection implementation
Run this to verify all components are correctly set up
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from database import connect_to_mongo
from models import Assignment, CustomDockerImage, Teacher

async def verify_implementation():
    """Verify the Docker image selection implementation"""
    
    print("🔍 Verifying Docker Image Selection Implementation\n")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    # Check 1: Assignment model has custom_docker_image_id field
    print("\n1️⃣ Checking Assignment Model...")
    assignment_fields = Assignment.__fields__.keys()
    if 'custom_docker_image_id' in assignment_fields:
        print("   ✅ Assignment has custom_docker_image_id field")
    else:
        print("   ❌ Assignment missing custom_docker_image_id field")
    
    # Check 2: Teacher exists
    print("\n2️⃣ Checking Teacher Account...")
    teacher = await Teacher.find_one()
    if teacher:
        print(f"   ✅ Found teacher: {teacher.email}")
        teacher_id = str(teacher.id)
    else:
        print("   ❌ No teacher found - run: python -m scripts.seed_users")
        return
    
    # Check 3: Docker images exist
    print("\n3️⃣ Checking Docker Images...")
    images = await CustomDockerImage.find(
        CustomDockerImage.teacher_id == teacher_id
    ).to_list()
    
    if images:
        print(f"   ✅ Found {len(images)} Docker images")
        uploaded = [img for img in images if img.status == 'uploaded']
        print(f"   ✅ {len(uploaded)} images are uploaded and ready")
        
        for img in uploaded[:3]:  # Show first 3
            print(f"      • {img.name} ({img.base_image})")
    else:
        print("   ⚠️  No Docker images found")
        print("      Run: python backend/test_data/load_sample_docker_images.py")
    
    # Check 4: Assignment with custom image
    print("\n4️⃣ Checking Assignments with Custom Images...")
    assignments = await Assignment.find(
        Assignment.teacher_id == teacher_id
    ).to_list()
    
    if assignments:
        with_image = [a for a in assignments if a.custom_docker_image_id]
        print(f"   ✅ Found {len(assignments)} assignments")
        print(f"   ✅ {len(with_image)} use custom Docker images")
        
        if with_image:
            for assignment in with_image[:3]:
                img = await CustomDockerImage.get(assignment.custom_docker_image_id)
                img_name = img.name if img else "Unknown"
                print(f"      • {assignment.title} → {img_name}")
    else:
        print("   ℹ️  No assignments yet - create one via UI")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY\n")
    
    all_checks_passed = (
        'custom_docker_image_id' in assignment_fields and
        teacher and
        len(images) > 0
    )
    
    if all_checks_passed:
        print("✅ All components are set up correctly!")
        print("\n🎯 Next Steps:")
        print("   1. Start backend: python main.py")
        print("   2. Start frontend: npm run dev")
        print("   3. Login as teacher")
        print("   4. Create assignment with custom Docker image")
    else:
        print("⚠️  Some components need attention")
        print("\n🔧 Actions Required:")
        if not teacher:
            print("   • Create teacher: python -m scripts.seed_users")
        if len(images) == 0:
            print("   • Load sample images: python backend/test_data/load_sample_docker_images.py")
    
    print()

if __name__ == "__main__":
    asyncio.run(verify_implementation())
