"""
TestCase model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, Any

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

class SingleCellTestCase(Document):
    """Model for single-cell testcase functions that evaluate student submissions"""
    assignment_id: Indexed(str)  # Reference to Assignment document ID
    question_number: int
    cell_id: str  # Notebook cell identifier
    testcase_name: str  # Name/description of the testcase
    testcase_function: str  # Python function code to evaluate the submission
    test_args: Optional[list[Any]] = None  # Arguments to pass to student's function
    expected_output: Optional[Any] = None  # Expected output/result
    timeout: int = 5  # Timeout in seconds for execution
    language: str = "python"  # Programming language
    points: float = 1.0  # Points awarded if testcase passes
    description: Optional[str] = None  # Additional description
    
    class Settings:
        name = "single_cell_test_cases"
        indexes = [
            "assignment_id",
            [("assignment_id", 1), ("question_number", 1)],
            [("assignment_id", 1), ("cell_id", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "507f1f77bcf86cd799439011",
                "question_number": 1,
                "cell_id": "cell_1",
                "testcase_name": "test_circle_area",
                "testcase_function": "def test_circle_area(submission): ...",
                "timeout": 5,
                "language": "python",
                "points": 10.0,
                "description": "Test circle area calculation"
            }
        }
