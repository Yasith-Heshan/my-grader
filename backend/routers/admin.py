"""
Admin router: account creation, grading oversight, user management
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

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


@router.post("/create-teacher", status_code=status.HTTP_201_CREATED)
async def create_teacher(
    payload: CreateTeacherRequest, admin: Admin = Depends(get_current_admin)
):
    """Admin creates a new teacher account"""
    existing = await teacher_service.get_teacher_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Teacher already exists")

    teacher = await admin_service.create_teacher(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    return {
        "id": str(teacher.id),
        "name": teacher.name,
        "email": teacher.email,
        "message": "Teacher account created successfully",
    }


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
