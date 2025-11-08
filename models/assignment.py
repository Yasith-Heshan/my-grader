"""
Assignment model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime

class Assignment(Document):
    title: Indexed(str)
    description: Optional[str] = None
    teacher_id: Indexed(str)  # Reference to Teacher document ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    
    class Settings:
        name = "assignments"
        indexes = [
            "teacher_id",
            "created_at",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python Basics Assignment",
                "description": "Introduction to Python programming",
                "teacher_id": "507f1f77bcf86cd799439011",
                "due_date": "2025-12-31T23:59:59"
            }
        }
