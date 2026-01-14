"""
Script to create sample assignments for testing
This script loads the JSON files and creates assignments in the database
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from beanie import PydanticObjectId
from database import connect_to_mongo
from models import Assignment, Teacher, CustomDockerImage

async def create_sample_assignments():
    """Create sample assignments from JSON files"""
    
    print("📝 Creating Sample Assignments\n")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    # Get teacher
    teacher = await Teacher.find_one()
    if not teacher:
        print("❌ No teacher found. Run: python -m scripts.seed_users")
        return
    
    teacher_id = str(teacher.id)
    print(f"✅ Using teacher: {teacher.email}\n")
    
    # Get Docker images for assignments that need them
    docker_images = await CustomDockerImage.find(
        CustomDockerImage.teacher_id == teacher_id,
        CustomDockerImage.status == "uploaded"
    ).to_list()
    
    image_map = {}
    if docker_images:
        print(f"✅ Found {len(docker_images)} uploaded Docker images")
        for img in docker_images:
            if "numpy" in img.name.lower() or "scientific" in img.name.lower():
                image_map['numpy'] = str(img.id)
            elif "machine learning" in img.name.lower() or "ml" in img.name.lower():
                image_map['ml'] = str(img.id)
        print()
    
    # Assignment files to load
    assignment_files = [
        ('assignment_python_basics.json', None),
        ('assignment_data_structures.json', None),
        ('assignment_functions.json', None),
        ('assignment_data_science.json', 'numpy'),
        ('assignment_machine_learning.json', 'ml'),
    ]
    
    created_count = 0
    skipped_count = 0
    
    for filename, image_key in assignment_files:
        json_file = Path(__file__).parent / filename
        
        if not json_file.exists():
            print(f"⚠️  Skipped: {filename} (file not found)")
            skipped_count += 1
            continue
        
        # Load JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Replace teacher_id
        data['teacher_id'] = teacher_id
        
        # Replace docker image ID if needed
        if image_key:
            if image_key in image_map:
                data['custom_docker_image_id'] = image_map[image_key]
                print(f"📦 {data['title']}")
                print(f"   → Using Docker image: {image_key}")
            else:
                print(f"⚠️  {data['title']}")
                print(f"   → Skipped (no {image_key} Docker image found)")
                print(f"   → Run: python backend/test_data/load_sample_docker_images.py")
                skipped_count += 1
                continue
        else:
            print(f"📄 {data['title']}")
            print(f"   → Using default Python image")
        
        # Check if assignment already exists
        existing = await Assignment.find_one(
            Assignment.title == data['title'],
            Assignment.teacher_id == teacher_id
        )
        
        if existing:
            print(f"   ⏭️  Already exists (ID: {existing.id})\n")
            skipped_count += 1
            continue
        
        # Create assignment
        try:
            # Convert questions to proper format
            questions_data = []
            for q in data['questions']:
                questions_data.append({
                    'question_number': q['question_number'],
                    'title': q['title'],
                    'description': q['description'],
                    'cell_id': q['cell_id'],
                    'points': q['points'],
                    'starter_code': q.get('starter_code', '# Write your code here\n')
                })
            
            assignment = Assignment(
                title=data['title'],
                description=data['description'],
                questions=questions_data,
                teacher_id=teacher_id,
                due_date=datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')),
                custom_docker_image_id=data.get('custom_docker_image_id'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            await assignment.insert()
            print(f"   ✅ Created (ID: {assignment.id})")
            print(f"   Questions: {len(questions_data)}")
            print(f"   Total Points: {sum(q['points'] for q in questions_data)}\n")
            created_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
            skipped_count += 1
    
    # Summary
    print("=" * 60)
    print(f"✅ Created: {created_count} assignments")
    print(f"⏭️  Skipped: {skipped_count} assignments")
    
    if created_count > 0:
        print("\n🎉 Sample assignments ready for testing!")
        print("\n📋 Next Steps:")
        print("   1. Login as teacher")
        print("   2. View assignments list")
        print("   3. Edit or create new assignments")
        print("   4. Test with student submissions")

if __name__ == "__main__":
    asyncio.run(create_sample_assignments())
