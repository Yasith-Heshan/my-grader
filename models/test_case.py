"""
TestCase model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional

class TestCase(Document):
    assignment_id: Indexed(str)  # Reference to Assignment document ID
    question_number: int
    cell_id: str  # Notebook cell identifier
    test_code: str  # Python code to execute for testing
    expected_output: Optional[str] = None  # Expected output (optional)
    points: float = 1.0
    description: Optional[str] = None
    
    class Settings:
        name = "test_cases"
        indexes = [
            "assignment_id",
            [("assignment_id", 1), ("question_number", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "507f1f77bcf86cd799439011",
                "question_number": 1,
                "cell_id": "cell_1",
                "test_code": "passed = result == 42",
                "points": 10.0,
                "description": "Calculate 6 * 7"
            }
        }
