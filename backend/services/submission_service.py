"""
Submission service - Business logic for submission operations
"""
from typing import List, Optional
from beanie import PydanticObjectId
from models import Submission, SubmissionItem, GradeStatus
from models.submission import CellAnswer
from schemas import SubmissionCreate, SubmissionItemCreate

async def create_submission(submission: SubmissionCreate) -> Submission:
    """Create a new submission"""
    # Convert answers from schema to model format
    answers = []
    if submission.answers:
        answers = [
            CellAnswer(
                cell_id=answer.cell_id,
                code=answer.code,
                score=0.0,
                max_score=0.0
            )
            for answer in submission.answers
        ]
    
    db_submission = Submission(
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        code=submission.code,  # Legacy field
        answers=answers,  # Multi-question answers
        status=GradeStatus.PENDING
    )
    await db_submission.insert()
    return db_submission

async def get_submission(submission_id: str) -> Optional[Submission]:
    """Get submission by ID"""
    return await Submission.get(PydanticObjectId(submission_id))

async def get_all_submissions() -> List[Submission]:
    """Get all submissions"""
    return await Submission.find_all().to_list()

async def get_submissions_by_assignment(assignment_id: str) -> List[Submission]:
    """Get all submissions for an assignment"""
    return await Submission.find(Submission.assignment_id == assignment_id).to_list()

async def get_student_submissions(
    student_id: str,
    assignment_id: Optional[str] = None
) -> List[Submission]:
    """Get all submissions for a student"""
    query = Submission.find(Submission.student_id == student_id)
    
    if assignment_id:
        query = Submission.find(
            Submission.student_id == student_id,
            Submission.assignment_id == assignment_id
        )
    
    return await query.to_list()

async def add_submission_item(
    submission_id: str,
    item: SubmissionItemCreate
) -> SubmissionItem:
    """Add a submission item (cell code) to a submission"""
    # Check if item already exists for this test case
    existing_item = await SubmissionItem.find_one(
        SubmissionItem.submission_id == submission_id,
        SubmissionItem.test_case_id == item.test_case_id
    )
    
    if existing_item:
        # Update existing item
        existing_item.submitted_code = item.submitted_code
        existing_item.cell_id = item.cell_id
        await existing_item.save()
        return existing_item
    
    # Create new item
    db_item = SubmissionItem(
        submission_id=submission_id,
        test_case_id=item.test_case_id,
        cell_id=item.cell_id,
        submitted_code=item.submitted_code
    )
    await db_item.insert()
    return db_item

async def get_submission_items(submission_id: str) -> List[SubmissionItem]:
    """Get all submission items for a submission"""
    return await SubmissionItem.find(
        SubmissionItem.submission_id == submission_id
    ).to_list()

async def get_assignment_submissions(assignment_id: str) -> List[Submission]:
    """Get all submissions for an assignment"""
    return await Submission.find(
        Submission.assignment_id == assignment_id
    ).to_list()
