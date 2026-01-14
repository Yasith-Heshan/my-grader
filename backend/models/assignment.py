"""
Assignment model
"""
from beanie import Document, Indexed
from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import datetime

class Question(BaseModel):
    """Embedded question within an assignment"""
    question_number: int
    title: str
    description: str  # Markdown formatted question text
    cell_id: str  # Unique identifier for the code cell
    points: float = 10.0
    starter_code: Optional[str] = "# Write your code here\n"

class Assignment(Document):
    title: Indexed(str)
    description: Optional[str] = None
    questions: List[Question] = Field(default_factory=list)
    teacher_id: Indexed(str)  # Reference to Teacher document ID
    custom_docker_image_id: Optional[str] = None  # Link to CustomDockerImage
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
