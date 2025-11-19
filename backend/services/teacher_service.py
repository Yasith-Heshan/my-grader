"""
Teacher service - Business logic for teacher operations
"""
from typing import Optional, List
from beanie import PydanticObjectId
from models import Teacher, SingleCellTestCase, Assignment
from schemas.test_case import SingleCellTestCaseCreate
from schemas import TeacherCreate

async def create_teacher(teacher: TeacherCreate) -> Teacher:
    """Create a new teacher"""
    # Check if teacher with email already exists
    existing = await Teacher.find_one(Teacher.email == teacher.email)
    if existing:
        raise ValueError(f"Teacher with email {teacher.email} already exists")
    
    db_teacher = Teacher(
        name=teacher.name,
        email=teacher.email
    )
    await db_teacher.insert()
    return db_teacher

async def get_teacher(teacher_id: str) -> Optional[Teacher]:
    """Get teacher by ID"""
    return await Teacher.get(PydanticObjectId(teacher_id))

async def get_teacher_by_email(email: str) -> Optional[Teacher]:
    """Get teacher by email"""
    return await Teacher.find_one(Teacher.email == email)

async def create_single_cell_testcase(testcase_data: SingleCellTestCaseCreate) -> SingleCellTestCase:
    """
    Create a new single-cell testcase function for evaluating student submissions
    
    Args:
        testcase_data: SingleCellTestCaseCreate schema with testcase details
        
    Returns:
        Created SingleCellTestCase document
        
    Raises:
        ValueError: If assignment doesn't exist or testcase validation fails
    """
    # Verify assignment exists
    assignment = await Assignment.get(PydanticObjectId(testcase_data.assignment_id))
    if not assignment:
        raise ValueError(f"Assignment with ID {testcase_data.assignment_id} not found")
    
    # Create the testcase document
    testcase = SingleCellTestCase(
        assignment_id=testcase_data.assignment_id,
        question_number=testcase_data.question_number,
        cell_id=testcase_data.cell_id,
        testcase_name=testcase_data.testcase_name,
        testcase_function=testcase_data.testcase_function,
        test_args=testcase_data.test_args,
        expected_output=testcase_data.expected_output,
        timeout=testcase_data.timeout,
        language=testcase_data.language,
        points=testcase_data.points,
        description=testcase_data.description
    )
    
    await testcase.insert()
    return testcase

async def get_single_cell_testcase(testcase_id: str) -> Optional[SingleCellTestCase]:
    """Get single-cell testcase by ID"""
    return await SingleCellTestCase.get(PydanticObjectId(testcase_id))

async def get_testcases_for_assignment(assignment_id: str) -> List[SingleCellTestCase]:
    """Get all single-cell testcases for an assignment"""
    return await SingleCellTestCase.find(
        SingleCellTestCase.assignment_id == assignment_id
    ).to_list()

async def get_testcases_for_cell(assignment_id: str, cell_id: str) -> List[SingleCellTestCase]:
    """Get all single-cell testcases for a specific cell in an assignment"""
    return await SingleCellTestCase.find(
        SingleCellTestCase.assignment_id == assignment_id,
        SingleCellTestCase.cell_id == cell_id
    ).to_list()

async def delete_single_cell_testcase(testcase_id: str) -> bool:
    """Delete a single-cell testcase by ID"""
    testcase = await SingleCellTestCase.get(PydanticObjectId(testcase_id))
    if testcase:
        await testcase.delete()
        return True
    return False
