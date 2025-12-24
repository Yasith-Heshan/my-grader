"""
Seed test teachers and students into MongoDB
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import models and services
sys.path.insert(0, str(Path(__file__).parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Teacher, Student, Admin
from utils.security import hash_password
from config import settings


async def seed_test_users():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    await init_beanie(
        database=db,
        document_models=[Teacher, Student, Admin]
    )
    print(f"Connected to MongoDB")

    try:
        # Check and create test teachers
        test_teachers = [
            {
                "name": "Dr. Alice Johnson",
                "email": "alice@example.com",
                "password": "teacher123",
            },
            {
                "name": "Prof. Bob Smith",
                "email": "bob@example.com",
                "password": "teacher456",
            },
        ]

        for teacher_data in test_teachers:
            existing = await Teacher.find_one(Teacher.email == teacher_data["email"])
            if existing:
                print(f"Teacher already exists: {teacher_data['email']}")
            else:
                teacher = Teacher(
                    name=teacher_data["name"],
                    email=teacher_data["email"],
                    password_hash=hash_password(teacher_data["password"]),
                )
                await teacher.insert()
                print(f"Created teacher: {teacher_data['email']}")

        # Check and create test students
        test_students = [
            {
                "name": "John Doe",
                "email": "john@student.com",
                "student_number": "S001",
                "password": "student123",
            },
            {
                "name": "Jane Smith",
                "email": "jane@student.com",
                "student_number": "S002",
                "password": "student456",
            },
            {
                "name": "Mike Johnson",
                "email": "mike@student.com",
                "student_number": "S003",
                "password": "student789",
            },
        ]

        for student_data in test_students:
            existing = await Student.find_one(Student.email == student_data["email"])
            if existing:
                print(f"Student already exists: {student_data['email']}")
            else:
                student = Student(
                    name=student_data["name"],
                    email=student_data["email"],
                    student_number=student_data["student_number"],
                    password_hash=hash_password(student_data["password"]),
                )
                await student.insert()
                print(f"Created student: {student_data['email']}")

        print("\nTest data seeding complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("Closed MongoDB connection")


if __name__ == "__main__":
    asyncio.run(seed_test_users())
