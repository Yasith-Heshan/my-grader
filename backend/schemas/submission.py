"""
Submission Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CellAnswerCreate(BaseModel):
    """Answer for a single question cell"""
    cell_id: str
    code: str

class CellAnswerResponse(BaseModel):
    """Response for a single question cell answer"""
    cell_id: str
    code: str
    score: float = 0.0
    max_score: float = 0.0
    feedback: Optional[str] = None
    
    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    assignment_id: str
    student_id: Optional[str] = None  # Optional - will use mock student if not provided
    code: Optional[str] = None  # Legacy: Single code field for backward compatibility
    answers: Optional[List[CellAnswerCreate]] = None  # Multi-question answers

class SubmissionItemCreate(BaseModel):
    test_case_id: str
    cell_id: str = Field(..., min_length=1, max_length=100)
    submitted_code: str = Field(..., min_length=1)

class SubmissionItemResponse(BaseModel):
    id: str = Field(..., alias="_id")
    submission_id: str
    test_case_id: str
    cell_id: str
    submitted_code: str
    output: Optional[str]
    score: float
    max_score: float
    passed: bool
    feedback: Optional[str]
    graded_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        populate_by_name = True

class SubmissionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    assignment_id: str
    student_id: str
    code: Optional[str] = None  # Legacy field
    answers: List[CellAnswerResponse] = []  # Multi-question answers
    status: str
    graded: bool = False
    total_score: float = 0.0
    max_score: float = 0.0
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    items: List[SubmissionItemResponse] = []
    
    class Config:
        from_attributes = True
        populate_by_name = True

class GradingResult(BaseModel):
    submission_id: str
    status: str
    total_score: float
    max_score: float
    percentage: float
    passed_items: int
    total_items: int
    items: List[SubmissionItemResponse]
    message: str
