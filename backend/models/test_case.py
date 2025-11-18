"""
TestCase model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime

class TestCase(Document):
    assignment_id: Indexed(str)  # Reference to Assignment document ID
    test_name: str  # Unique name for the test
    question_number: Optional[int] = None  # Optional question number
    cell_id: Optional[str] = None  # Optional notebook cell identifier
    
    # Support for both code-based and function-based tests
    test_code: Optional[str] = None  # Python code to execute for testing (legacy/simple tests)
    serialized_function: Optional[str] = None  # Base64 encoded pickled test function (advanced tests)
    
    expected_output: Optional[str] = None  # Expected output (optional)
    points: float = 1.0
    description: Optional[str] = None
    timeout: float = 30.0  # Maximum execution time in seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "test_cases"
        indexes = [
            "assignment_id",
            [("assignment_id", 1), ("question_number", 1)],
            [("assignment_id", 1), ("test_name", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "507f1f77bcf86cd799439011",
                "test_name": "circle_area_test",
                "question_number": 1,
                "cell_id": "cell_1",
                "test_code": "passed = result == 42",
                "points": 10.0,
                "timeout": 30.0,
                "description": "Calculate 6 * 7"
            }
        }
