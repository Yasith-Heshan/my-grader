"""
TestCase Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any

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

class SingleCellTestCaseCreate(BaseModel):
    """Schema for adding a single-cell testcase function to evaluate student submissions"""
    assignment_id: str = Field(..., min_length=1, description="Assignment ID this testcase belongs to")
    question_number: int = Field(..., ge=1, description="Question number within the assignment")
    cell_id: str = Field(..., min_length=1, max_length=100, description="Notebook cell identifier")
    testcase_name: str = Field(..., min_length=1, max_length=200, description="Name/description of the testcase")
    testcase_function: str = Field(..., min_length=1, description="Python function code to evaluate the submission")
    test_args: Optional[list[Any]] = Field(default=None, description="Arguments to pass to the student's function")
    expected_output: Optional[Any] = Field(default=None, description="Expected output/result from the function")
    timeout: Optional[int] = Field(default=5, ge=1, le=60, description="Timeout in seconds for execution")
    language: str = Field(default="python", pattern="^(python|python3)$", description="Programming language")
    points: float = Field(default=1.0, ge=0, description="Points awarded if testcase passes")
    description: Optional[str] = Field(default=None, description="Additional description or context")

class SingleCellTestCaseResponse(BaseModel):
    """Response schema for single-cell testcase"""
    id: str = Field(..., alias="_id")
    assignment_id: str
    question_number: int
    cell_id: str
    testcase_name: str
    testcase_function: str
    test_args: Optional[list[Any]]
    expected_output: Optional[Any]
    timeout: int
    language: str
    points: float
    description: Optional[str]
    
    class Config:
        from_attributes = True
        populate_by_name = True

class CellEvaluationRequest(BaseModel):
    """Request schema for evaluating a single cell"""
    assignment_id: str = Field(..., min_length=1, description="Assignment ID")
    cell_id: str = Field(..., min_length=1, description="Cell identifier")
    student_code: str = Field(..., min_length=1, description="Student's code to evaluate")
    timeout: Optional[int] = Field(default=None, ge=1, le=60, description="Optional timeout override")

class TestCaseResult(BaseModel):
    """Result of a single testcase execution"""
    testcase_name: str
    passed: bool
    score: float
    max_score: float
    feedback: str

class CellEvaluationResponse(BaseModel):
    """Response schema for cell evaluation"""
    success: bool
    score: float
    max_score: float
    percentage: float = 0.0
    passed_tests: int = 0
    total_tests: int = 0
    feedback: str
    student_output: str = ""
    results: list[TestCaseResult]
