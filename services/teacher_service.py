"""
Teacher service - Business logic for teacher operations
"""
from typing import Optional
from beanie import PydanticObjectId
from models import Teacher
from schemas import TeacherCreate

async def create_teacher(teacher: TeacherCreate) -> Teacher:
    """Create a new teacher"""
    # Check if teacher with email already exists
    existing = await Teacher.find_one(Teacher.email == teacher.email)
    if existing:
        raise ValueError(f"Teacher with email {teacher.email} already exists")
    
    db_teacher = Teacher(
        name=teacher.name,
        email=teacher.email
    )
    await db_teacher.insert()
    return db_teacher

async def get_teacher(teacher_id: str) -> Optional[Teacher]:
    """Get teacher by ID"""
    return await Teacher.get(PydanticObjectId(teacher_id))

async def get_teacher_by_email(email: str) -> Optional[Teacher]:
    """Get teacher by email"""
    return await Teacher.find_one(Teacher.email == email)
