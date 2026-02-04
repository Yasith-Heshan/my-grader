from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

class TeacherResponse(BaseModel):
    id: str
    name: str
    email: str
    message: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Teacher account created successfully",
                "created_at": "2026-02-04T10:30:00Z"
            }
        }  

class CreateTeacherRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Teacher's full name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=50, description="Strong password")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name contains only valid characters"""
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets security requirements"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@university.edu",
                "password": "SecurePass123"
            }
        }