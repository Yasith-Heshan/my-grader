"""
User Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class TeacherCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr

class TeacherResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    student_number: Optional[str] = Field(None, max_length=50)

class StudentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: str
    student_number: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
