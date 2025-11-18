"""
Assignment service - Business logic for assignment operations
Enhanced with support for dynamic test functions (LocalGrader style)
"""
from typing import List, Optional, Callable
import pickle
import base64
from beanie import PydanticObjectId
from models import Assignment, TestCase
from schemas import AssignmentCreate, TestCaseCreate

async def create_assignment(assignment: AssignmentCreate) -> Assignment:
    """Create a new assignment"""
    db_assignment = Assignment(
        title=assignment.title,
        description=assignment.description,
        teacher_id=assignment.teacher_id,
        due_date=assignment.due_date
    )
    await db_assignment.insert()
    return db_assignment

async def get_assignment(assignment_id: str) -> Optional[Assignment]:
    """Get assignment by ID"""
    return await Assignment.get(PydanticObjectId(assignment_id))

async def list_assignments(
    teacher_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Assignment]:
    """List assignments, optionally filtered by teacher"""
    query = Assignment.find()
    
    if teacher_id:
        query = Assignment.find(Assignment.teacher_id == teacher_id)
    
    return await query.skip(skip).limit(limit).to_list()

async def add_test_cases(
    assignment_id: str,
    test_cases: List[TestCaseCreate]
) -> List[TestCase]:
    """Add test cases to an assignment"""
    db_test_cases = []
    
    for tc in test_cases:
        db_test_case = TestCase(
            assignment_id=assignment_id,
            question_number=tc.question_number,
            cell_id=tc.cell_id,
            test_code=tc.test_code,
            expected_output=tc.expected_output,
            points=tc.points,
            description=tc.description
        )
        await db_test_case.insert()
        db_test_cases.append(db_test_case)
    
    return db_test_cases

async def add_test_case_with_function(
    assignment_id: str,
    test_name: str,
    test_function: Callable,
    points: float,
    description: str = "",
    timeout: float = 30.0,
    question_number: Optional[int] = None
) -> TestCase:
    """
    Add a test case with a dynamic test function (LocalGrader style)
    
    Args:
        assignment_id: ID of the assignment
        test_name: Unique name for the test
        test_function: Python function that tests student code
        points: Points awarded for passing this test
        description: Human-readable description
        timeout: Maximum time allowed for test execution
        question_number: Optional question number
        
    Returns:
        Created TestCase document
        
    Example:
        # Create a test function
        def test_circle_area(submission):
            if 'circle_area' not in submission:
                return {"score": 0, "feedback": "Function not found"}
            # ... test logic ...
            return {"score": 1.0, "feedback": "Perfect!"}
        
        # Add it to assignment
        test_case = await add_test_case_with_function(
            assignment_id="...",
            test_name="circle_area_test",
            test_function=test_circle_area,
            points=10.0,
            description="Test circle area calculation"
        )
    """
    # Serialize test function
    serialized_function = base64.b64encode(pickle.dumps(test_function)).decode('utf-8')
    
    # Create test case
    db_test_case = TestCase(
        assignment_id=assignment_id,
        test_name=test_name,
        question_number=question_number,
        serialized_function=serialized_function,
        points=points,
        description=description,
        timeout=timeout
    )
    await db_test_case.insert()
    
    return db_test_case

async def get_test_cases(assignment_id: str) -> List[TestCase]:
    """Get all test cases for an assignment"""
    return await TestCase.find(
        TestCase.assignment_id == assignment_id
    ).sort(+TestCase.question_number).to_list()

async def get_test_case(test_case_id: str) -> Optional[TestCase]:
    """Get a specific test case by ID"""
    return await TestCase.get(PydanticObjectId(test_case_id))
