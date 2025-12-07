"""
User models: Teacher and Student
"""

from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime


class Teacher(Document):
    name: str
    email: Indexed(EmailStr, unique=True)
    # Optional password hash for authentication
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "teachers"
        indexes = [
            "email",
        ]

    class Config:
        json_schema_extra = {
            "example": {"name": "Dr. Smith", "email": "smith@university.edu"}
        }


class Student(Document):
    name: str
    email: Indexed(EmailStr, unique=True)
    # Optional password hash for authentication
    password_hash: Optional[str] = None
    student_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "students"
        indexes = [
            "email",
            "student_number",
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alice Johnson",
                "email": "alice@student.edu",
                "student_number": "S12345",
            }
        }
