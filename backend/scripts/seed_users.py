"""Seed script to create sample teacher and student accounts.

Run from repository root (recommended venv activated):

python backend/scripts/seed_users.py

The script will connect to MongoDB using the same settings as the app,
create two users if they don't already exist, and print the results.
"""

import asyncio
import os
import sys

# Ensure backend package imports work when running the script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import connect_to_mongo, close_mongo_connection
from models import Teacher, Student
from utils.security import hash_password


async def seed():
    await connect_to_mongo()
    try:
        # Sample teacher
        t_email = "teacher@example.com"
        existing_t = await Teacher.find_one(Teacher.email == t_email)
        if existing_t:
            print(f"Teacher already exists: {t_email} -> id={existing_t.id}")
        else:
            teacher = Teacher(
                name="Sample Teacher",
                email=t_email,
                password_hash=hash_password("teacher123"),
            )
            await teacher.insert()
            print(f"Created teacher: {t_email} -> id={teacher.id}")

        # Sample student
        s_email = "student@example.com"
        existing_s = await Student.find_one(Student.email == s_email)
        if existing_s:
            print(f"Student already exists: {s_email} -> id={existing_s.id}")
        else:
            student = Student(
                name="Sample Student",
                email=s_email,
                student_number="S100",
                password_hash=hash_password("student123"),
            )
            await student.insert()
            print(f"Created student: {s_email} -> id={student.id}")

    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed())
