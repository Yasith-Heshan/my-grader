"""
Assignment Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    teacher_id: str
    due_date: Optional[datetime] = None

class AssignmentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    description: Optional[str]
    teacher_id: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    
    class Config:
        from_attributes = True
        populate_by_name = True

class StudentResult(BaseModel):
    student_id: str
    student_name: str
    total_score: float
    max_score: float
    percentage: float
    status: str
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]

class AssignmentSummary(BaseModel):
    assignment_id: str
    assignment_title: str
    total_submissions: int
    graded_submissions: int
    pending_submissions: int
    average_score: float
    students: List[StudentResult]
    
    class Config:
        from_attributes = True
