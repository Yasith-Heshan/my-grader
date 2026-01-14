"""
Load sample student submissions for testing
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from beanie import PydanticObjectId
from database import connect_to_mongo
from models import Assignment, Submission, SubmissionItem, Student, GradeStatus

async def create_sample_submissions():
    """Create sample student submissions from JSON file"""
    
    print("📝 Creating Sample Student Submissions\n")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    
    # Load sample submissions
    json_file = Path(__file__).parent / "sample_submissions.json"
    with open(json_file, 'r') as f:
        submissions_data = json.load(f)
    
    # Get or create a test student
    student = await Student.find_one(Student.email == "student1@example.com")
    if not student:
        print("⚠️  Creating test student: student1@example.com")
        student = Student(
            email="student1@example.com",
            full_name="Test Student",
            hashed_password="$2b$12$dummy_hash",
            created_at=datetime.utcnow()
        )
        await student.insert()
    
    student_id = str(student.id)
    print(f"✅ Using student: {student.email}\n")
    
    # Get an assignment to submit to
    assignment = await Assignment.find_one()
    if not assignment:
        print("❌ No assignments found. Create one first:")
        print("   python backend/test_data/create_sample_assignments.py")
        return
    
    assignment_id = str(assignment.id)
    print(f"✅ Using assignment: {assignment.title}\n")
    
    created_count = 0
    
    # Group submissions by student email
    submissions_by_email = {}
    for sub_data in submissions_data:
        email = sub_data['student_email']
        if email not in submissions_by_email:
            submissions_by_email[email] = []
        submissions_by_email[email].append(sub_data)
    
    # Create submissions
    for email, items in submissions_by_email.items():
        # Check if submission already exists
        existing = await Submission.find_one(
            Submission.student_id == student_id,
            Submission.assignment_id == assignment_id
        )
        
        if existing:
            print(f"⏭️  Skipped {email}: Already has submission for this assignment\n")
            continue
        
        # Create submission with first item's code
        first_item = items[0]
        
        submission = Submission(
            assignment_id=assignment_id,
            student_id=student_id,
            code=first_item['submitted_code'],
            status=GradeStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await submission.insert()
        
        print(f"✅ Created submission for {email}")
        print(f"   Assignment: {assignment.title}")
        print(f"   Code preview: {first_item['submitted_code'][:50]}...")
        print(f"   Status: {first_item['status']}")
        print()
        
        created_count += 1
    
    # Summary
    print("=" * 60)
    print(f"✅ Created {created_count} sample submissions")
    
    if created_count > 0:
        print("\n📋 Next Steps:")
        print("   1. Login as teacher")
        print("   2. View submission list")
        print("   3. Grade submissions")
        print("   4. Check grading results")

async def show_submission_examples():
    """Show example submission codes"""
    
    print("\n" + "="*60)
    print("SUBMISSION CODE EXAMPLES")
    print("="*60)
    
    examples = {
        "Perfect Answer (10 points)": """import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

# Test
radius = 5
area = calculate_circle_area(radius)
print(f"Area of circle with radius {radius} is {area:.2f}")""",

        "Good Answer with validation (10 points)": """import math

def calculate_circle_area(radius):
    if radius < 0:
        return 0
    return math.pi * radius ** 2

test_cases = [5, 10, 3.5, -2]
for r in test_cases:
    print(f"Radius {r}: Area = {calculate_circle_area(r):.2f}")""",

        "Simple correct answer (10 points)": """def calculate_circle_area(radius):
    pi = 3.14159
    return pi * radius * radius

radius = 5
area = calculate_circle_area(radius)
print(f"Area: {area}")""",

        "Wrong formula (0 points)": """def calculate_circle_area(radius):
    return 2 * 3.14159 * radius  # WRONG: This is circumference!

radius = 5
area = calculate_circle_area(radius)
print(f"Area: {area}")""",

        "Missing import (Error)": """def calculate_circle_area(radius):
    return math.pi * radius ** 2  # ERROR: math not imported

radius = 5
print(calculate_circle_area(radius))""",
    }
    
    for title, code in examples.items():
        print(f"\n{title}:")
        print("-" * 40)
        print(code)
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        asyncio.run(show_submission_examples())
    else:
        print("Sample Student Submissions")
        print("="*60)
        print("Options:")
        print("  python load_sample_submissions.py          # Load submissions")
        print("  python load_sample_submissions.py --examples  # Show code examples")
        print()
        
        response = input("Load sample submissions? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(create_sample_submissions())
        else:
            asyncio.run(show_submission_examples())
