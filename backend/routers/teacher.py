"""
Teacher API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from beanie import PydanticObjectId, Document

from schemas import (
    AssignmentCreate, AssignmentResponse, AssignmentSummary,
    QuestionCreate, TestCaseResponse, GradingResult,
    TeacherCreate, TeacherResponse
)
from schemas.test_case import SingleCellTestCaseCreate, SingleCellTestCaseResponse
from services import assignment_service, grader_service, teacher_service
from middleware.auth import get_current_teacher
from models import Teacher
from config.docker_presets import DOCKER_IMAGE_PRESETS

router = APIRouter()

def serialize_document(doc: Document) -> dict:
    """Convert Beanie Document to dict with ObjectId as string"""
    data = doc.model_dump()
    if doc.id:
        data["_id"] = str(doc.id)
        data["id"] = str(doc.id)  # Add id alias for frontend compatibility
    # Ensure questions are included for Assignment documents
    if hasattr(doc, 'questions') and doc.questions:
        data["questions"] = [q.model_dump() if hasattr(q, 'model_dump') else q for q in doc.questions]
    return data

def serialize_documents(docs: List[Document]) -> List[dict]:
    """Convert list of Beanie Documents to list of dicts"""
    return [serialize_document(doc) for doc in docs]

# Teacher Management
@router.post("/register", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def register_teacher(teacher: TeacherCreate):
    """Register a new teacher"""
    try:
        result = await teacher_service.create_teacher(teacher)
        return serialize_document(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register teacher: {str(e)}")

@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(teacher_id: str):
    """Get teacher by ID"""
    try:
        teacher = await teacher_service.get_teacher(teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return teacher
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get teacher: {str(e)}")


@router.get("/teachers", response_model=List[TeacherResponse])
async def list_teachers_endpoint(skip: int = 0, limit: int = 100):
    """List all teachers"""
    try:
        teachers = await teacher_service.list_teachers(skip, limit)
        return serialize_documents(teachers)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list teachers: {str(e)}")

# Docker Image Presets
@router.get("/docker-presets")
async def get_docker_presets():
    """Get available Docker image presets for assignments"""
    return {"presets": DOCKER_IMAGE_PRESETS}

# Assignment Management
@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_all_assignments():
    """Get all assignments"""
    try:
        assignments = await assignment_service.get_all_assignments()
        return serialize_documents(assignments)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get assignments: {str(e)}")

@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    teacher: Teacher = Depends(get_current_teacher)
):
    """Create a new assignment"""
    try:
        result = await assignment_service.create_assignment(assignment)
        return serialize_document(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create assignment: {str(e)}")

@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: str):
    """Get assignment by ID"""
    try:
        assignment = await assignment_service.get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get assignment: {str(e)}")

@router.get("/assignments/{assignment_id}/submissions")
async def get_assignment_submissions(assignment_id: str):
    """Get all submissions for an assignment"""
    try:
        from services import submission_service
        submissions = await submission_service.get_submissions_by_assignment(assignment_id)
        return serialize_documents(submissions)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get submissions: {str(e)}")

@router.get("/assignments", response_model=List[AssignmentResponse])
async def list_assignments(
    teacher_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List all assignments, optionally filtered by teacher"""
    try:
        return await assignment_service.list_assignments(teacher_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list assignments: {str(e)}")

@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: str,
    teacher: Teacher = Depends(get_current_teacher)
):
    """Delete an assignment"""
    try:
        await assignment_service.delete_assignment(assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete assignment: {str(e)}")

# Question/TestCase Management
@router.post("/assignments/{assignment_id}/questions", 
             response_model=List[TestCaseResponse],
             status_code=status.HTTP_201_CREATED)
async def add_questions(
    assignment_id: str,
    questions: QuestionCreate,
):
    """Add questions and test cases to an assignment"""
    try:
        assignment = await assignment_service.get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        result = await assignment_service.add_test_cases(assignment_id, questions.test_cases)
        return serialize_documents(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add questions: {str(e)}")

@router.get("/assignments/{assignment_id}/questions", response_model=List[TestCaseResponse])
async def get_questions(assignment_id: str):
    """Get all questions/test cases for an assignment"""
    try:
        assignment = await assignment_service.get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        return await assignment_service.get_test_cases(assignment_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get questions: {str(e)}")

# Grading
@router.post("/submissions/{submission_id}/grade", response_model=dict)
async def grade_submission(
    submission_id: str,
    teacher: Teacher = Depends(get_current_teacher)
):
    """Grade a single submission"""
    try:
        result = await grader_service.grade_submission(submission_id)
        return {
            "submission_id": submission_id,
            "status": "success",
            "message": "Submission graded successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to grade submission: {str(e)}")

@router.post("/assignments/{assignment_id}/grade", response_model=dict)
async def grade_assignment(assignment_id: str):
    """Trigger grading for all submissions of an assignment"""
    try:
        assignment = await assignment_service.get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        results = await grader_service.grade_assignment_submissions(assignment_id)
        
        return {
            "assignment_id": assignment_id,
            "total_submissions": len(results),
            "graded": sum(1 for r in results if r["status"] == "completed"),
            "message": f"Graded {len(results)} submissions"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to grade assignment: {str(e)}")

# Results and Summary
@router.get("/assignments/{assignment_id}/summary", response_model=AssignmentSummary)
async def get_assignment_summary(assignment_id: str):
    """Get summarized grading results for an assignment"""
    try:
        assignment = await assignment_service.get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        return await grader_service.get_assignment_summary(assignment_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get assignment summary: {str(e)}")

@router.get("/assignments/{assignment_id}/students/{student_id}/results", 
            response_model=GradingResult)
async def get_student_results(
    assignment_id: str,
    student_id: str,
):
    """Get grading results for a specific student on an assignment"""
    submission = await grader_service.get_student_submission(assignment_id, student_id)
    if not submission:
        raise HTTPException(
            status_code=404,
            detail="No submission found for this student and assignment"
        )
    
    return await grader_service.get_grading_result(str(submission.id))

# Single-Cell TestCase Management
@router.post("/testcases", response_model=SingleCellTestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_testcase(testcase: SingleCellTestCaseCreate):
    """Create a new single-cell testcase function for evaluating student submissions"""
    try:
        result = await teacher_service.create_single_cell_testcase(testcase)
        return serialize_document(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create testcase: {str(e)}")

@router.get("/testcases/{testcase_id}", response_model=SingleCellTestCaseResponse)
async def get_testcase(testcase_id: str):
    """Get a single-cell testcase by ID"""
    try:
        testcase = await teacher_service.get_single_cell_testcase(testcase_id)
        if not testcase:
            raise HTTPException(status_code=404, detail="Testcase not found")
        return serialize_document(testcase)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get testcase: {str(e)}")

@router.get("/assignments/{assignment_id}/testcases", response_model=List[SingleCellTestCaseResponse])
async def get_assignment_testcases(assignment_id: str):
    """Get all single-cell testcases for an assignment"""
    try:
        testcases = await teacher_service.get_testcases_for_assignment(assignment_id)
        return serialize_documents(testcases)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get testcases: {str(e)}")

@router.get("/testcases/cell/{assignment_id}/{cell_id}", response_model=List[SingleCellTestCaseResponse])
async def get_cell_testcases(assignment_id: str, cell_id: str):
    """Get all single-cell testcases for a specific cell in an assignment"""
    try:
        testcases = await teacher_service.get_testcases_for_cell(assignment_id, cell_id)
        return serialize_documents(testcases)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get cell testcases: {str(e)}")

@router.delete("/testcases/{testcase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_testcase(testcase_id: str):
    """Delete a single-cell testcase"""
    try:
        deleted = await teacher_service.delete_single_cell_testcase(testcase_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Testcase not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete testcase: {str(e)}")
