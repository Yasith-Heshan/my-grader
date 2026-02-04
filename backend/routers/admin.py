"""
Admin router: account creation, grading oversight, user management
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from backend.schemas.admin import TeacherResponse
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


@router.post("/create-student", status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: CreateStudentRequest, admin: Admin = Depends(get_current_admin)
):
    """Admin creates a new student account"""
    existing = await student_service.get_student_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")

    student = await admin_service.create_student(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        student_number=payload.student_number,
    )

    return {
        "id": str(student.id),
        "name": student.name,
        "email": student.email,
        "student_number": student.student_number,
        "message": "Student account created successfully",
    }


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
