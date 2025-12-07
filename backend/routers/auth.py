from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from services import teacher_service, student_service
from models import Teacher, Student
from utils.security import hash_password, verify_password, create_access_token, decode_access_token
from config import settings

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


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    # create teacher or student
    if payload.role == 'teacher':
        existing = await teacher_service.get_teacher_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=400, detail='Teacher already exists')

        teacher = Teacher(name=payload.name, email=payload.email, password_hash=hash_password(payload.password))
        await teacher.insert()
        token = create_access_token(subject=str(teacher.id))
        return {"user": {"id": str(teacher.id), "name": teacher.name, "email": teacher.email, "role": "teacher"}, "token": token}

    if payload.role == 'student':
        existing = await student_service.get_student_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=400, detail='Student already exists')

        student = Student(name=payload.name, email=payload.email, student_number=payload.student_number, password_hash=hash_password(payload.password))
        await student.insert()
        token = create_access_token(subject=str(student.id))
        return {"user": {"id": str(student.id), "name": student.name, "email": student.email, "role": "student"}, "token": token}

    raise HTTPException(status_code=400, detail='Invalid role')


@router.post('/login')
async def login(payload: LoginRequest):
    # If role provided, try specific collection first
    if payload.role == 'teacher':
        teacher = await teacher_service.get_teacher_by_email(payload.email)
        if not teacher or not teacher.password_hash:
            raise HTTPException(status_code=401, detail='Invalid credentials')
        if not verify_password(payload.password, teacher.password_hash):
            raise HTTPException(status_code=401, detail='Invalid credentials')
        token = create_access_token(subject=str(teacher.id))
        return {"user": {"id": str(teacher.id), "name": teacher.name, "email": teacher.email, "role": "teacher"}, "token": token}

    if payload.role == 'student':
        student = await student_service.get_student_by_email(payload.email)
        if not student or not student.password_hash:
            raise HTTPException(status_code=401, detail='Invalid credentials')
        if not verify_password(payload.password, student.password_hash):
            raise HTTPException(status_code=401, detail='Invalid credentials')
        token = create_access_token(subject=str(student.id))
        return {"user": {"id": str(student.id), "name": student.name, "email": student.email, "role": "student"}, "token": token}

    # If no role specified, try both
    teacher = await teacher_service.get_teacher_by_email(payload.email)
    if teacher and teacher.password_hash and verify_password(payload.password, teacher.password_hash):
        token = create_access_token(subject=str(teacher.id))
        return {"user": {"id": str(teacher.id), "name": teacher.name, "email": teacher.email, "role": "teacher"}, "token": token}

    student = await student_service.get_student_by_email(payload.email)
    if student and student.password_hash and verify_password(payload.password, student.password_hash):
        token = create_access_token(subject=str(student.id))
        return {"user": {"id": str(student.id), "name": student.name, "email": student.email, "role": "student"}, "token": token}

    raise HTTPException(status_code=401, detail='Invalid credentials')


@router.get('/me')
async def me(request: Request):
    auth = request.headers.get('authorization')
    if not auth:
        raise HTTPException(status_code=401, detail='Missing authorization header')
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(status_code=401, detail='Invalid authorization header')
    token = parts[1]
    try:
        payload = decode_access_token(token)
        sub = payload.get('sub')
        if not sub:
            raise HTTPException(status_code=401, detail='Invalid token')

        # Try teacher then student
        try:
            teacher = await teacher_service.get_teacher(sub)
        except Exception:
            teacher = None

        if teacher:
            return {"id": str(teacher.id), "name": teacher.name, "email": teacher.email, "role": "teacher"}

        try:
            student = await student_service.get_student(sub)
        except Exception:
            student = None

        if student:
            return {"id": str(student.id), "name": student.name, "email": student.email, "role": "student"}

        raise HTTPException(status_code=404, detail='User not found')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail='Could not validate credentials')


@router.post('/logout')
async def logout():
    # stateless tokens: just return success; frontend will clear token
    return {"message": "logged out"}
