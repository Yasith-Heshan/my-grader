"""
Grader service - Business logic for grading operations
Enhanced with LocalGrader functionality for dynamic test execution
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId
import sys
import pickle
import base64
import time
import traceback
from io import StringIO

from models import Submission, SubmissionItem, TestCase, GradeStatus, Student, Assignment
from schemas import GradingResult, SubmissionItemResponse, StudentResult, AssignmentSummary


def _run_test_with_timeout(test_function, submission_data: Dict, timeout: float):
    """
    Run a test function with timeout protection
    
    Args:
        test_function: The test to run
        submission_data: Student's submission data
        timeout: Maximum execution time
        
    Returns:
        Test result
    """
    start_time = time.time()
    result = test_function(submission_data)
    if time.time() - start_time > timeout:
        raise TimeoutError("Test execution timed out")
    return result


def grade_single_cell(
    test_case: TestCase,
    submission_item: SubmissionItem
) -> Dict[str, Any]:
    """
    Grade a single cell submission against a test case.
    Supports both code-based tests and function-based tests with advanced features like:
    - Partial credit
    - Detailed feedback
    - Timeout handling
    """
    try:
        # Prepare submission data
        namespace = {}
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Execute student's submitted code
        try:
            exec(submission_item.submitted_code, namespace)
        except Exception as e:
            sys.stdout = old_stdout
            return {
                'passed': False,
                'score': 0.0,
                'max_score': test_case.points,
                'output': '',
                'feedback': f'Error executing student code: {str(e)}\n{traceback.format_exc()}'
            }
        
        # Get the output from student code
        student_output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Now run the test
        start_time = time.time()
        
        # Check if test uses serialized function (advanced LocalGrader style)
        if test_case.serialized_function:
            try:
                # Deserialize test function
                serialized_data = base64.b64decode(test_case.serialized_function.encode('utf-8'))
                test_function = pickle.loads(serialized_data)
                
                # Run test with timeout
                test_result = _run_test_with_timeout(
                    test_function, namespace, test_case.timeout
                )
                
                execution_time = time.time() - start_time
                
                # Process different result formats
                if test_result is True:
                    # Full credit
                    score = test_case.points
                    passed = True
                    feedback = "Test passed successfully"
                    
                elif isinstance(test_result, (int, float)) and 0 <= test_result <= 1:
                    # Partial credit (test returned a score between 0 and 1)
                    score = test_case.points * test_result
                    passed = test_result == 1.0
                    feedback = f"Partial credit: {test_result*100:.1f}%"
                    
                elif isinstance(test_result, dict) and "score" in test_result:
                    # Detailed result with score and feedback
                    score = test_case.points * test_result.get("score", 0)
                    passed = test_result.get("score", 0) >= 1.0
                    feedback = str(test_result.get("feedback", "No feedback provided"))
                    
                else:
                    # Test failed
                    score = 0.0
                    passed = False
                    feedback = str(test_result) if test_result is not None else "Test failed"
                
                return {
                    'passed': passed,
                    'score': score,
                    'max_score': test_case.points,
                    'output': student_output,
                    'feedback': feedback,
                    'execution_time': execution_time
                }
                
            except TimeoutError:
                return {
                    'passed': False,
                    'score': 0.0,
                    'max_score': test_case.points,
                    'output': student_output,
                    'feedback': f"Test timed out after {test_case.timeout} seconds",
                    'execution_time': test_case.timeout
                }
                
            except Exception as e:
                return {
                    'passed': False,
                    'score': 0.0,
                    'max_score': test_case.points,
                    'output': student_output,
                    'feedback': f'Error executing test function: {str(e)}\n{traceback.format_exc()}',
                    'execution_time': time.time() - start_time
                }
        
        # Legacy code-based test (simple pass/fail)
        elif test_case.test_code:
            try:
                # Execute test code in the same namespace
                exec(test_case.test_code, namespace)
                
                # Check if test passed (test_code should set 'passed' variable)
                passed = namespace.get('passed', False)
                
                # Calculate score
                score = test_case.points if passed else 0.0
                
                # Generate feedback
                feedback = namespace.get('feedback', 'Test executed successfully' if passed else 'Test failed')
                
                return {
                    'passed': passed,
                    'score': score,
                    'max_score': test_case.points,
                    'output': student_output,
                    'feedback': feedback,
                    'execution_time': time.time() - start_time
                }
                
            except Exception as e:
                return {
                    'passed': False,
                    'score': 0.0,
                    'max_score': test_case.points,
                    'output': student_output,
                    'feedback': f'Error executing test code: {str(e)}\n{traceback.format_exc()}',
                    'execution_time': time.time() - start_time
                }
        
        else:
            return {
                'passed': False,
                'score': 0.0,
                'max_score': test_case.points,
                'output': student_output,
                'feedback': 'No test code or test function found for this test case',
                'execution_time': 0.0
            }
        
    except Exception as e:
        # Restore stdout
        sys.stdout = old_stdout
        
        return {
            'passed': False,
            'score': 0.0,
            'max_score': test_case.points,
            'output': '',
            'feedback': f'Unexpected error: {str(e)}\n{traceback.format_exc()}',
            'execution_time': 0.0
        }

async def grade_submission(submission_id: str) -> GradingResult:
    """Grade a full submission by grading all its items"""
    submission = await Submission.get(PydanticObjectId(submission_id))
    
    if not submission:
        raise ValueError(f"Submission {submission_id} not found")
    
    # Update status to grading
    submission.status = GradeStatus.GRADING
    await submission.save()
    
    # Get all submission items
    items = await SubmissionItem.find(
        SubmissionItem.submission_id == str(submission.id)
    ).to_list()
    
    total_score = 0.0
    max_score = 0.0
    passed_count = 0
    
    # Grade each item
    for item in items:
        # Get associated test case
        test_case = await TestCase.get(PydanticObjectId(item.test_case_id))
        
        if not test_case:
            continue
        
        # Grade the item
        result = grade_single_cell(test_case, item)
        
        # Update submission item with results
        item.passed = result['passed']
        item.score = result['score']
        item.max_score = result['max_score']
        item.output = result['output']
        item.feedback = result['feedback']
        item.graded_at = datetime.utcnow()
        await item.save()
        
        # Accumulate totals
        total_score += result['score']
        max_score += result['max_score']
        passed_count += 1 if result['passed'] else 0
    
    # Update submission with total scores
    submission.total_score = total_score
    submission.max_score = max_score
    submission.status = GradeStatus.COMPLETED
    submission.graded_at = datetime.utcnow()
    await submission.save()
    
    # Prepare response
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Convert items to response format
    item_responses = []
    for item in items:
        item_dict = item.model_dump()
        item_dict['_id'] = str(item.id)
        item_responses.append(SubmissionItemResponse(**item_dict))
    
    return GradingResult(
        submission_id=str(submission.id),
        status=submission.status.value,
        total_score=total_score,
        max_score=max_score,
        percentage=percentage,
        passed_items=passed_count,
        total_items=len(items),
        items=item_responses,
        message=f"Graded {len(items)} items. Score: {total_score}/{max_score} ({percentage:.1f}%)"
    )

async def grade_assignment_submissions(assignment_id: str) -> List[Dict[str, Any]]:
    """Grade all submissions for an assignment"""
    submissions = await Submission.find(
        Submission.assignment_id == assignment_id
    ).to_list()
    
    results = []
    
    for submission in submissions:
        try:
            result = await grade_submission(str(submission.id))
            results.append({
                "submission_id": str(submission.id),
                "student_id": submission.student_id,
                "status": "completed",
                "score": result.total_score,
                "max_score": result.max_score
            })
        except Exception as e:
            submission.status = GradeStatus.FAILED
            await submission.save()
            results.append({
                "submission_id": str(submission.id),
                "student_id": submission.student_id,
                "status": "failed",
                "error": str(e)
            })
    
    return results

async def get_grading_result(submission_id: str) -> GradingResult:
    """Get grading results for a submission"""
    submission = await Submission.get(PydanticObjectId(submission_id))
    
    if not submission:
        raise ValueError(f"Submission {submission_id} not found")
    
    items = await SubmissionItem.find(
        SubmissionItem.submission_id == str(submission.id)
    ).to_list()
    
    passed_count = sum(1 for item in items if item.passed)
    percentage = (submission.total_score / submission.max_score * 100) if submission.max_score > 0 else 0
    
    # Convert items to response format
    item_responses = []
    for item in items:
        item_dict = item.model_dump()
        item_dict['_id'] = str(item.id)
        item_responses.append(SubmissionItemResponse(**item_dict))
    
    return GradingResult(
        submission_id=str(submission.id),
        status=submission.status.value,
        total_score=submission.total_score,
        max_score=submission.max_score,
        percentage=percentage,
        passed_items=passed_count,
        total_items=len(items),
        items=item_responses,
        message=f"Submission grading {submission.status.value}"
    )

async def get_student_submission(
    assignment_id: str,
    student_id: str
) -> Optional[Submission]:
    """Get a student's submission for an assignment"""
    return await Submission.find_one(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_id
    )

async def get_assignment_summary(assignment_id: str) -> AssignmentSummary:
    """Get summarized grading results for an assignment"""
    assignment = await Assignment.get(PydanticObjectId(assignment_id))
    
    if not assignment:
        raise ValueError(f"Assignment {assignment_id} not found")
    
    submissions = await Submission.find(
        Submission.assignment_id == assignment_id
    ).to_list()
    
    total_submissions = len(submissions)
    graded_submissions = sum(1 for s in submissions if s.status == GradeStatus.COMPLETED)
    pending_submissions = sum(1 for s in submissions if s.status == GradeStatus.PENDING)
    
    # Calculate average score
    completed = [s for s in submissions if s.status == GradeStatus.COMPLETED and s.max_score > 0]
    average_score = sum(s.total_score / s.max_score * 100 for s in completed) / len(completed) if completed else 0.0
    
    # Prepare student results
    student_results = []
    for submission in submissions:
        student = await Student.get(PydanticObjectId(submission.student_id))
        percentage = (submission.total_score / submission.max_score * 100) if submission.max_score > 0 else 0
        
        student_results.append(StudentResult(
            student_id=str(submission.student_id),
            student_name=student.name if student else "Unknown",
            total_score=submission.total_score,
            max_score=submission.max_score,
            percentage=percentage,
            status=submission.status.value,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at
        ))
    
    return AssignmentSummary(
        assignment_id=str(assignment.id),
        assignment_title=assignment.title,
        total_submissions=total_submissions,
        graded_submissions=graded_submissions,
        pending_submissions=pending_submissions,
        average_score=average_score,
        students=student_results
    )
