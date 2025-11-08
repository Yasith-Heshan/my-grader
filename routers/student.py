"""
Student API routes
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from schemas import (
    SubmissionCreate, SubmissionResponse, SubmissionItemCreate,
    SubmissionItemResponse, GradingResult,
    StudentCreate, StudentResponse, AssignmentResponse
)
from services import submission_service, student_service, assignment_service

router = APIRouter()

# Student Management
@router.post("/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def register_student(student: StudentCreate):
    """Register a new student"""
    return await student_service.create_student(student)

@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    """Get student by ID"""
    student = await student_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Assignment Browsing
@router.get("/assignments", response_model=List[AssignmentResponse])
async def list_available_assignments(
    skip: int = 0,
    limit: int = 100,
):
    """List all available assignments"""
    return await assignment_service.list_assignments(None, skip, limit)

@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment_details(assignment_id: str):
    """Get assignment details"""
    assignment = await assignment_service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

# Submission Management
@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(submission: SubmissionCreate):
    """Create a new submission for an assignment"""
    # Verify assignment exists
    assignment = await assignment_service.get_assignment(submission.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify student exists
    student = await student_service.get_student(submission.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return await submission_service.create_submission(submission)

@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(submission_id: str):
    """Get submission by ID"""
    submission = await submission_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.get("/students/{student_id}/submissions", response_model=List[SubmissionResponse])
async def get_student_submissions(
    student_id: str,
    assignment_id: Optional[str] = None,
):
    """Get all submissions for a student, optionally filtered by assignment"""
    return await submission_service.get_student_submissions(student_id, assignment_id)

# Submit Code for Cells
@router.post("/submissions/{submission_id}/items",
             response_model=SubmissionItemResponse,
             status_code=status.HTTP_201_CREATED)
async def submit_cell_code(
    submission_id: str,
    item: SubmissionItemCreate,
):
    """Submit code for a specific cell (maps cell_id to test_case)"""
    submission = await submission_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return await submission_service.add_submission_item(submission_id, item)

@router.get("/submissions/{submission_id}/items", response_model=List[SubmissionItemResponse])
async def get_submission_items(submission_id: str):
    """Get all submitted items for a submission"""
    submission = await submission_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return await submission_service.get_submission_items(submission_id)

# Grading Results
@router.get("/submissions/{submission_id}/results", response_model=GradingResult)
async def get_submission_results(submission_id: str):
    """Retrieve grading results for a submission"""
    submission = await submission_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    from services import grader_service
    return await grader_service.get_grading_result(submission_id)
