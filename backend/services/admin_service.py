"""
Admin service for admin-specific operations: account creation, grading, etc.
"""

from asyncio.log import logger
from backend.exeptions import DuplicateResourceError
from backend.services import teacher_service
from backend.utils.security import hash_password
from models import Teacher, Student, Admin
from typing import List


async def get_admin(admin_id: str) -> Admin:
    """Fetch admin by ID"""
    return await Admin.get(admin_id)


async def get_admin_by_email(email: str) -> Admin | None:
    """Fetch admin by email"""
    return await Admin.find_one(Admin.email == email)


async def list_admins(skip: int = 0, limit: int = 10) -> List[Admin]:
    """List all admins with pagination"""
    return await Admin.find().skip(skip).limit(limit).to_list()

# ToDo: Remove this function
async def create_teacher(
    name: str, email: str, password_hash: str, **kwargs
) -> Teacher:
    """Admin creates a teacher account"""
    teacher = Teacher(name=name, email=email, password_hash=password_hash, **kwargs)
    await teacher.insert()
    return teacher

async def create_teacher_actount(
        name: str,
        email: str,
        password: str
)->Teacher:
    """
    Create a new teacher account
    
    Args:
        name: Teacher's full name
        email: Teacher's email (must be unique)
        password: Plain text password (will be hashed)
    
    Returns:
        Teacher: Created teacher object
        
    Raises:
        DuplicateResourceError: If teacher already exists
    """
    # check uniqueness
    existing = await teacher_service.get_teacher_by_email(email)
    if existing:
        raise DuplicateResourceError("Teacher", email)
    # Hash password
    password_hash = hash_password(password)
    teacher = Teacher(
        name=name,
        email=email,
        password_hash=password_hash,
    )
    await teacher.insert()
    logger.info(f"Created new teacher account: {email}")
    return teacher



async def create_student(
    name: str, email: str, password_hash: str, student_number: str = None, **kwargs
) -> Student:
    """Admin creates a student account"""
    student = Student(
        name=name,
        email=email,
        password_hash=password_hash,
        student_number=student_number,
        **kwargs
    )
    await student.insert()
    return student
