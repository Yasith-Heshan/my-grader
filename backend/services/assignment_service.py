"""
Assignment service - Business logic for assignment operations
"""
from typing import List, Optional
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

async def get_all_assignments() -> List[Assignment]:
    """Get all assignments"""
    return await Assignment.find_all().to_list()

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

async def delete_assignment(assignment_id: str) -> None:
    """Delete an assignment and its related data"""
    assignment = await Assignment.get(PydanticObjectId(assignment_id))
    if not assignment:
        raise ValueError(f"Assignment with id {assignment_id} not found")
    
    # Delete related test cases
    await TestCase.find(TestCase.assignment_id == assignment_id).delete()
    
    # Delete the assignment
    await assignment.delete()

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

async def get_test_cases(assignment_id: str) -> List[TestCase]:
    """Get all test cases for an assignment"""
    return await TestCase.find(
        TestCase.assignment_id == assignment_id
    ).sort(+TestCase.question_number).to_list()

async def get_test_case(test_case_id: str) -> Optional[TestCase]:
    """Get a specific test case by ID"""
    return await TestCase.get(PydanticObjectId(test_case_id))
