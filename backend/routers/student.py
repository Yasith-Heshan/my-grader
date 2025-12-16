"""
Student API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from beanie import Document

from schemas import (
    SubmissionCreate, SubmissionResponse, SubmissionItemCreate,
    SubmissionItemResponse, GradingResult,
    StudentCreate, StudentResponse, AssignmentResponse
)
from schemas.test_case import CellEvaluationRequest, CellEvaluationResponse
from services import submission_service, student_service, assignment_service, grader_service
from middleware.auth import get_current_student, RoleChecker
from models import Student

router = APIRouter()

def serialize_document(doc: Document) -> dict:
    """Convert Beanie Document to dict with ObjectId as string"""
    data = doc.model_dump()
    if doc.id:
        data["_id"] = str(doc.id)
        data["id"] = str(doc.id)  # Add id alias for frontend compatibility
    # Add graded field for Submission documents
    if hasattr(doc, 'status') and hasattr(doc, 'graded'):
        data["graded"] = doc.graded
    # Ensure questions are included for Assignment documents
    if hasattr(doc, 'questions') and doc.questions:
        data["questions"] = [q.model_dump() if hasattr(q, 'model_dump') else q for q in doc.questions]
    return data

def serialize_documents(docs: List[Document]) -> List[dict]:
    """Convert list of Beanie Documents to list of dicts"""
    return [serialize_document(doc) for doc in docs]

# Student Management
@router.post("/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def register_student(student: StudentCreate):
    """Register a new student"""
    try:
        result = await student_service.create_student(student)
        return serialize_document(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register student: {str(e)}")

@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    """Get student by ID"""
    try:
        student = await student_service.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get student: {str(e)}")


@router.get("/students", response_model=List[StudentResponse])
async def list_students_endpoint(skip: int = 0, limit: int = 100):
    """List all students"""
    try:
        students = await student_service.list_students(skip, limit)
        return serialize_documents(students)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list students: {str(e)}")

# Assignment Browsing
@router.get("/assignments", response_model=List[AssignmentResponse])
async def list_available_assignments(
    skip: int = 0,
    limit: int = 100,
):
    """List all available assignments"""
    try:
        assignments = await assignment_service.list_assignments(None, skip, limit)
        return serialize_documents(assignments)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list assignments: {str(e)}")

@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment_details(assignment_id: str):
    """Get assignment details"""
    assignment = await assignment_service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return serialize_document(assignment)

# Submission Management
@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(submission: SubmissionCreate):
    """Create a new submission for an assignment"""
    try:
        # Verify assignment exists
        assignment = await assignment_service.get_assignment(submission.assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Use mock student_id if not provided (for demo purposes)
        if not submission.student_id:
            submission.student_id = "mock_student_123"
        
        result = await submission_service.create_submission(submission)
        return serialize_document(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create submission: {str(e)}")

@router.get("/submissions/me", response_model=List[SubmissionResponse])
async def get_my_submissions():
    """Get all submissions for the current student (mock - returns all submissions)"""
    # In a real app, you'd get student_id from JWT token
    # For now, return all submissions
    submissions = await submission_service.get_all_submissions()
    return serialize_documents(submissions)

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
    
    return await grader_service.get_grading_result(submission_id)

# Single-Cell Evaluation
@router.post("/evaluate-cell", response_model=CellEvaluationResponse)
async def evaluate_cell(request: CellEvaluationRequest):
    """
    Evaluate a single cell of student code against testcase functions.
    This allows students to test their code before submitting the full assignment.
    """
    try:
        result = await grader_service.evaluate_single_cell(
            assignment_id=request.assignment_id,
            cell_id=request.cell_id,
            student_code=request.student_code,
            timeout=request.timeout
        )
        return CellEvaluationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate cell: {str(e)}"
        )
