"""
Admin service for admin-specific operations: account creation, grading, etc.
"""

from asyncio.log import logger
from backend.exeptions import DuplicateResourceError
from backend.services import student_service, teacher_service
from backend.utils.security import hash_password
from models import Teacher, Student, Admin
from typing import List, Optional


async def get_admin(admin_id: str) -> Admin:
    """Fetch admin by ID"""
    return await Admin.get(admin_id)


async def get_admin_by_email(email: str) -> Admin | None:
    """Fetch admin by email"""
    return await Admin.find_one(Admin.email == email)


async def list_admins(skip: int = 0, limit: int = 10) -> List[Admin]:
    """List all admins with pagination"""
    return await Admin.find().skip(skip).limit(limit).to_list()

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


# ToDo: Remove this function if not needed
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

async def create_student_account(
    name: str,
    email: str,
    password: str,  # Plain password
    student_number: Optional[str] = None
) -> Student:
    """
    Create a new student account
    
    Args:
        name: Student's full name
        email: Student's email (must be unique)
        password: Plain text password (will be hashed)
        student_number: Optional student ID number
    
    Returns:
        Student: Created student object
        
    Raises:
        DuplicateResourceError: If student already exists
    """
    # Check uniqueness by email
    existing = await student_service.get_student_by_email(email)
    if existing:
        raise DuplicateResourceError("Student", f"email={email}")
    
    # Check uniqueness by student number (if provided)
    if student_number:
        existing_by_number = await student_service.get_student_by_number(student_number)
        if existing_by_number:
            raise DuplicateResourceError("Student", f"student_number={student_number}")
    
    # Hash password in service layer
    password_hash = hash_password(password)
    
    # Create student
    student = Student(
        name=name,
        email=email,
        password_hash=password_hash,
        student_number=student_number
    )
    await student.save()
    
    # Log action
    logger.info(f"Student account created: {email}, number: {student_number}")
    
    return student
