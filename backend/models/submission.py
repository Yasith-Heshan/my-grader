"""
Submission and SubmissionItem models
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum

class GradeStatus(str, Enum):
    PENDING = "pending"
    GRADING = "grading"
    COMPLETED = "completed"
    FAILED = "failed"

class Submission(Document):
    assignment_id: Indexed(str)  # Reference to Assignment document ID
    student_id: Indexed(str)  # Reference to Student document ID
    code: Optional[str] = None  # Student's submitted code
    status: GradeStatus = GradeStatus.PENDING
    total_score: float = 0.0
    max_score: float = 0.0
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    graded_at: Optional[datetime] = None
    
    @property
    def graded(self) -> bool:
        """Check if submission is graded"""
        return self.status == GradeStatus.COMPLETED
    
    class Settings:
        name = "submissions"
        indexes = [
            "assignment_id",
            "student_id",
            [("assignment_id", 1), ("student_id", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "507f1f77bcf86cd799439011",
                "student_id": "507f1f77bcf86cd799439012",
                "status": "pending"
            }
        }

class SubmissionItem(Document):
    submission_id: Indexed(str)  # Reference to Submission document ID
    test_case_id: Indexed(str)  # Reference to TestCase document ID
    cell_id: str
    submitted_code: str
    output: Optional[str] = None
    score: float = 0.0
    max_score: float = 0.0
    passed: bool = False
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    
    class Settings:
        name = "submission_items"
        indexes = [
            "submission_id",
            "test_case_id",
            [("submission_id", 1), ("test_case_id", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "submission_id": "507f1f77bcf86cd799439013",
                "test_case_id": "507f1f77bcf86cd799439014",
                "cell_id": "cell_1",
                "submitted_code": "result = 6 * 7"
            }
        }
