"""
TestCase Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional

class TestCaseCreate(BaseModel):
    question_number: int = Field(..., ge=1)
    cell_id: str = Field(..., min_length=1, max_length=100)
    test_code: str = Field(..., min_length=1)
    expected_output: Optional[str] = None
    points: float = Field(default=1.0, ge=0)
    description: Optional[str] = None

class TestCaseResponse(BaseModel):
    id: str = Field(..., alias="_id")
    assignment_id: str
    question_number: int
    cell_id: str
    test_code: str
    expected_output: Optional[str]
    points: float
    description: Optional[str]
    
    class Config:
        from_attributes = True
        populate_by_name = True

class QuestionCreate(BaseModel):
    """Schema for adding questions with test cases to an assignment"""
    test_cases: list[TestCaseCreate]
