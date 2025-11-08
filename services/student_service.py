"""
Student service - Business logic for student operations
"""
from typing import Optional
from beanie import PydanticObjectId
from models import Student
from schemas import StudentCreate

async def create_student(student: StudentCreate) -> Student:
    """Create a new student"""
    # Check if student with email already exists
    existing = await Student.find_one(Student.email == student.email)
    if existing:
        raise ValueError(f"Student with email {student.email} already exists")
    
    db_student = Student(
        name=student.name,
        email=student.email,
        student_number=student.student_number
    )
    await db_student.insert()
    return db_student

async def get_student(student_id: str) -> Optional[Student]:
    """Get student by ID"""
    return await Student.get(PydanticObjectId(student_id))

async def get_student_by_email(email: str) -> Optional[Student]:
    """Get student by email"""
    return await Student.find_one(Student.email == email)
