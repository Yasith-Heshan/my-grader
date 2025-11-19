"""Quick test to check submissions in database"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import Submission, Assignment
from models.user import Student, Teacher

async def check_data():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(
        database=client.grading_system,
        document_models=[Submission, Assignment, Student, Teacher]
    )
    
    submissions = await Submission.find_all().to_list()
    assignments = await Assignment.find_all().to_list()
    students = await Student.find_all().to_list()
    teachers = await Teacher.find_all().to_list()
    
    print(f"\n=== Database Contents ===")
    print(f"Total submissions: {len(submissions)}")
    print(f"Total assignments: {len(assignments)}")
    print(f"Total students: {len(students)}")
    print(f"Total teachers: {len(teachers)}")
    
    if submissions:
        print("\nSubmissions:")
        for s in submissions:
            print(f"  - ID: {s.id}, Assignment: {s.assignment_id}, Student: {s.student_id}")
    else:
        print("\n⚠️ No submissions found in database - this is why the endpoint returns []")
    
    if assignments:
        print("\nAssignments:")
        for a in assignments:
            print(f"  - ID: {a.id}, Title: {a.title}")
    
    if students:
        print("\nStudents:")
        for u in students:
            print(f"  - ID: {u.id}, Name: {u.name}, Email: {u.email}")

if __name__ == "__main__":
    asyncio.run(check_data())
