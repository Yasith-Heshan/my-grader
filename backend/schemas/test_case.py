"""
TestCase Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TestCaseCreate(BaseModel):
    question_number: Optional[int] = Field(None, ge=1)
    cell_id: Optional[str] = Field(None, min_length=1, max_length=100)
    test_code: Optional[str] = Field(None, min_length=1)
    test_name: Optional[str] = Field(None, min_length=1, max_length=200)
    serialized_function: Optional[str] = None
    expected_output: Optional[str] = None
    points: float = Field(default=1.0, ge=0)
    description: Optional[str] = None
    timeout: float = Field(default=30.0, ge=1, le=300)

class TestCaseResponse(BaseModel):
    id: str = Field(..., alias="_id")
    assignment_id: str
    test_name: Optional[str] = None
    question_number: Optional[int] = None
    cell_id: Optional[str] = None
    test_code: Optional[str] = None
    serialized_function: Optional[str] = None
    expected_output: Optional[str] = None
    points: float
    description: Optional[str] = None
    timeout: float = 30.0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class QuestionCreate(BaseModel):
    """Schema for adding questions with test cases to an assignment"""
    test_cases: list[TestCaseCreate]
