"""
Admin router: account creation, grading oversight, user management
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from backend.schemas.admin import TeacherResponse
from backend.schemas.user import StudentResponse
from backend.services import audit_service
from services import admin_service, teacher_service, student_service, submission_service
from models import Admin
from utils.security import hash_password
from middleware.auth import get_current_admin

router = APIRouter()


class CreateTeacherRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)


class CreateStudentRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    student_number: Optional[str] = None


class GradeSubmissionRequest(BaseModel):
    score: float
    feedback: Optional[str] = None


@router.post(
        "/create-teacher",
          status_code=status.HTTP_201_CREATED,
          summary="Create a new teacher account",
          description="Admin endpoint to create a new teacher account"
)
async def create_teacher(
    request: CreateTeacherRequest, current_admin: Admin = Depends(get_current_admin)
)->TeacherResponse:
    """
    Create a new teacher account
    
    - **name**: Teacher's full name (2-100 chars)
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, mixed case, numbers)
    
    Returns the created teacher information
    """
    teacher = await admin_service.create_teacher_account(
        name=request.name,
        email=request.email,
        password=request.password  # Service will hash it
    )

    await audit_service.log_admin_action(
        admin_id=str(current_admin.id),
        action=audit_service.AuditAction.CREATE_TEACHER,
        resource_type=audit_service.ResourceType.TEACHER, 
        resource_id=str(teacher.id),
        details={"email": teacher.email, "name": teacher.name}
    )
    return TeacherResponse(
        id=str(teacher.id),
        name=teacher.name,
        email=teacher.email,
        message="Teacher account created successfully",
        created_at=teacher.created_at
    )


@router.post(
    "/create-student",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student account",
    description="Admin endpoint to create a new student with email, password, and optional student number"
)
async def create_student(
    request: CreateStudentRequest,  # Renamed from 'payload'
    current_admin: Admin = Depends(get_current_admin)  # Renamed from 'admin'
) -> StudentResponse:
    """
    Create a new student account
    
    - **name**: Student's full name (2-100 chars)
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, mixed case, numbers)
    - **student_number**: Optional student ID (alphanumeric, unique)
    
    Returns the created student information
    """
    # Service handles all business logic
    student = await admin_service.create_student_account(
        name=request.name,
        email=request.email,
        password=request.password,  # Service will hash it
        student_number=request.student_number
    )
    
    # Audit trail
    await audit_service.log_admin_action(
        admin_id=str(current_admin.id),
        action=audit_service.AuditAction.CREATE_STUDENT,
        resource_type=audit_service.ResourceType.STUDENT,
        resource_id=str(student.id),
        details={
            "email": student.email,
            "name": student.name,
            "student_number": student.student_number
        }
    )
    
    # Return structured response
    return StudentResponse(
        id=str(student.id),
        name=student.name,
        email=student.email,
        student_number=student.student_number,
        message="Student account created successfully",
        created_at=student.created_at
    )


@router.get("/submissions")
async def get_all_submissions(admin: Admin = Depends(get_current_admin)):
    """Admin views all student submissions"""
    submissions = await submission_service.get_submissions(skip=0, limit=1000)
    return submissions


@router.get("/assignments/all")
async def get_all_assignments(admin: Admin = Depends(get_current_admin)):
    """Admin views all assignments with details"""
    # Fetch all assignments (implementation depends on your submission_service)
    # For now, return a placeholder that can be extended
    return {"message": "All assignments view"}


@router.get("/students")
async def get_all_students(admin: Admin = Depends(get_current_admin)):
    """Admin views all students"""
    students = await student_service.list_students(skip=0, limit=1000)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "email": s.email,
            "student_number": s.student_number,
        }
        for s in students
    ]


@router.get("/teachers")
async def get_all_teachers(admin: Admin = Depends(get_current_admin)):
    """Admin views all teachers"""
    teachers = await teacher_service.list_teachers(skip=0, limit=1000)
    return [{"id": str(t.id), "name": t.name, "email": t.email} for t in teachers]
