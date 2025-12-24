from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from services import teacher_service, student_service, admin_service
from models import Teacher, Student, Admin
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from middleware.auth import get_current_user
from settings import settings

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(...)
    student_number: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = None


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    # create teacher or student
    if payload.role == "teacher":
        existing = await teacher_service.get_teacher_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=400, detail="Teacher already exists")

        teacher = Teacher(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        await teacher.insert()
        token = create_access_token(subject=str(teacher.id), role="teacher")
        return {
            "user": {
                "id": str(teacher.id),
                "name": teacher.name,
                "email": teacher.email,
                "role": "teacher",
            },
            "token": token,
        }

    if payload.role == "student":
        existing = await student_service.get_student_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=400, detail="Student already exists")

        student = Student(
            name=payload.name,
            email=payload.email,
            student_number=payload.student_number,
            password_hash=hash_password(payload.password),
        )
        await student.insert()
        token = create_access_token(subject=str(student.id), role="student")
        return {
            "user": {
                "id": str(student.id),
                "name": student.name,
                "email": student.email,
                "role": "student",
            },
            "token": token,
        }

    if payload.role == "admin":
        existing = await admin_service.get_admin_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=400, detail="Admin already exists")

        admin = Admin(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        await admin.insert()
        token = create_access_token(subject=str(admin.id), role="admin")
        return {
            "user": {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email,
                "role": "admin",
            },
            "token": token,
        }

    raise HTTPException(status_code=400, detail="Invalid role")


@router.post("/login")
async def login(payload: LoginRequest):
    # If role provided, try specific collection first
    if payload.role == "teacher":
        teacher = await teacher_service.get_teacher_by_email(payload.email)
        if not teacher or not teacher.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(payload.password, teacher.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(subject=str(teacher.id), role="teacher")
        return {
            "user": {
                "id": str(teacher.id),
                "name": teacher.name,
                "email": teacher.email,
                "role": "teacher",
            },
            "token": token,
        }

    if payload.role == "student":
        student = await student_service.get_student_by_email(payload.email)
        if not student or not student.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(payload.password, student.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(subject=str(student.id), role="student")
        return {
            "user": {
                "id": str(student.id),
                "name": student.name,
                "email": student.email,
                "role": "student",
            },
            "token": token,
        }

    if payload.role == "admin":
        admin = await admin_service.get_admin_by_email(payload.email)
        if not admin or not admin.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(payload.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(subject=str(admin.id), role="admin")
        return {
            "user": {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email,
                "role": "admin",
            },
            "token": token,
        }

    # If no role specified, try both
    teacher = await teacher_service.get_teacher_by_email(payload.email)
    if (
        teacher
        and teacher.password_hash
        and verify_password(payload.password, teacher.password_hash)
    ):
        token = create_access_token(subject=str(teacher.id), role="teacher")
        return {
            "user": {
                "id": str(teacher.id),
                "name": teacher.name,
                "email": teacher.email,
                "role": "teacher",
            },
            "token": token,
        }

    student = await student_service.get_student_by_email(payload.email)
    if (
        student
        and student.password_hash
        and verify_password(payload.password, student.password_hash)
    ):
        token = create_access_token(subject=str(student.id), role="student")
        return {
            "user": {
                "id": str(student.id),
                "name": student.name,
                "email": student.email,
                "role": "student",
            },
            "token": token,
        }

    admin = await admin_service.get_admin_by_email(payload.email)
    if (
        admin
        and admin.password_hash
        and verify_password(payload.password, admin.password_hash)
    ):
        token = create_access_token(subject=str(admin.id), role="admin")
        return {
            "user": {
                "id": str(admin.id),
                "name": admin.name,
                "email": admin.email,
                "role": "admin",
            },
            "token": token,
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    user_id = current_user["id"]
    role = current_user["role"]
    
    try:
        if role == "teacher":
            user = await teacher_service.get_teacher(user_id)
            if user:
                return {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "role": "teacher",
                }
        
        elif role == "student":
            user = await student_service.get_student(user_id)
            if user:
                return {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "role": "student",
                }
        
        elif role == "admin":
            user = await admin_service.get_admin(user_id)
            if user:
                return {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "role": "admin",
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


@router.post("/logout")
async def logout():
    # stateless tokens: just return success; frontend will clear token
    return {"message": "logged out"}
