"""
Grader service - Business logic for grading operations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId
import sys
from io import StringIO
import traceback
import signal
from contextlib import contextmanager

from models import Submission, SubmissionItem, TestCase, GradeStatus, Student, Assignment, SingleCellTestCase
from schemas import GradingResult, SubmissionItemResponse, StudentResult, AssignmentSummary
from utils.executor_factory import ExecutorFactory
from utils.executor_interface import ExecutionConfig, ExecutionLanguage

async def grade_single_cell(
    test_case: TestCase,
    submission_item: SubmissionItem
) -> Dict[str, Any]:
    """
    Grade a single cell submission against a test case using secure Docker execution.
    """
    try:
        # Create executor instance
        executor = await ExecutorFactory.get_default_executor()
        
        # Create execution configuration
        config = ExecutionConfig(
            timeout=10,
            memory_limit="256m",
            language=ExecutionLanguage.PYTHON
        )
        
        # Execute in Docker container (student code and test code separately)
        result = await executor.execute(
            student_code=submission_item.submitted_code,
            test_code=test_case.test_code,
            config_override=config
        )
        
        # Check if execution was successful
        if not result.success:
            return {
                'passed': False,
                'score': 0.0,
                'max_score': test_case.points,
                'output': result.stdout,
                'feedback': f'Execution error: {result.error_message or result.stderr}'
            }
        
        # Parse the result - test_code should print results in a specific format
        # or set variables that we can capture
        output = result.stdout
        
        # Try to determine if test passed from output or return value
        # The test code should output "PASSED" or set a variable
        passed = 'PASSED' in output.upper() or result.return_value == True
        
        # Calculate score
        score = test_case.points if passed else 0.0
        
        # Generate feedback
        feedback = output if output else ('Test passed' if passed else 'Test failed')
        
        return {
            'passed': passed,
            'score': score,
            'max_score': test_case.points,
            'output': output,
            'feedback': feedback
        }
        
    except Exception as e:
        return {
            'passed': False,
            'score': 0.0,
            'max_score': test_case.points,
            'output': '',
            'feedback': f'Error executing code: {str(e)}\n{traceback.format_exc()}'
        }

async def grade_submission(submission_id: str) -> GradingResult:
    """Grade a full submission by evaluating code against test cases"""
    submission = await Submission.get(PydanticObjectId(submission_id))
    
    if not submission:
        raise ValueError(f"Submission {submission_id} not found")
    
    # Update status to grading
    submission.status = GradeStatus.GRADING
    await submission.save()
    
    # Check if submission has code (single-cell submission)
    if submission.code:
        # Get all test cases for this assignment
        testcases = await SingleCellTestCase.find(
            SingleCellTestCase.assignment_id == submission.assignment_id
        ).to_list()
        
        if not testcases:
            submission.status = GradeStatus.COMPLETED
            submission.total_score = 0.0
            submission.max_score = 0.0
            submission.graded_at = datetime.utcnow()
            await submission.save()
            raise ValueError(f"No test cases found for assignment {submission.assignment_id}")
        
        # Evaluate against each test case
        total_score = 0.0
        max_score = 0.0
        
        for testcase in testcases:
            result = await evaluate_single_cell(
                assignment_id=submission.assignment_id,
                cell_id=testcase.cell_id,
                student_code=submission.code,
                timeout=testcase.timeout
            )
            
            total_score += result.get('score', 0.0)
            max_score += result.get('max_score', 0.0)
        
        # Update submission with scores
        submission.total_score = total_score
        submission.max_score = max_score
        submission.status = GradeStatus.COMPLETED
        submission.graded_at = datetime.utcnow()
        await submission.save()
        
        # Calculate percentage and message
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed_tests = 1 if total_score >= max_score * 0.7 else 0
        total_tests = 1
        
        return GradingResult(
            submission_id=str(submission.id),
            status="completed",
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            passed_items=passed_tests,
            total_items=total_tests,
            items=[],
            message=f"Grading completed. Score: {total_score:.1f}/{max_score:.1f} ({percentage:.1f}%)"
        )
    
    # Original code for multi-cell submissions with SubmissionItems
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
        
        # Grade the item (now async)
        result = await grade_single_cell(test_case, item)
        
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

# Single-Cell Evaluation Functions

class TimeoutException(Exception):
    """Exception raised when code execution times out"""
    pass

@contextmanager
def time_limit(seconds: int):
    """Context manager to limit execution time (Unix/Linux only)"""
    def signal_handler(signum, frame):
        raise TimeoutException("Code execution timed out")
    
    # Note: signal.alarm only works on Unix/Linux
    # For Windows, we'll use a different approach
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        # Windows fallback - no timeout enforcement
        yield

async def evaluate_single_cell(
    assignment_id: str,
    cell_id: str,
    student_code: str,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluate a single cell of student code against testcase functions
    
    Args:
        assignment_id: Assignment ID
        cell_id: Cell identifier
        student_code: Student's submitted code for the cell
        timeout: Optional timeout override (uses testcase timeout by default)
        
    Returns:
        Dict with evaluation results including score and feedback
    """
    # Get testcases for this cell
    testcases = await SingleCellTestCase.find(
        SingleCellTestCase.assignment_id == assignment_id,
        SingleCellTestCase.cell_id == cell_id
    ).to_list()
    
    if not testcases:
        return {
            "success": False,
            "score": 0.0,
            "max_score": 0.0,
            "feedback": f"No testcases found for cell '{cell_id}'",
            "results": []
        }
    
    # Create executor instance
    executor = await ExecutorFactory.get_default_executor()
    
    # Execute student code first to get variables/functions defined
    student_config = ExecutionConfig(
        timeout=timeout if timeout else 10,
        memory_limit="256m",
        language=ExecutionLanguage.PYTHON
    )
    
    # Execute student code with empty test code to just run it
    student_result = await executor.execute(
        student_code=student_code,
        test_code="# Student code executed above",
        config_override=student_config
    )
    student_output = student_result.stdout
    
    if not student_result.success:
        student_error = f"Error in student code: {student_result.error_message or student_result.stderr}"
        
        return {
            "success": False,
            "score": 0.0,
            "max_score": sum(tc.points for tc in testcases),
            "feedback": student_error,
            "student_output": student_output,
            "results": []
        }
    
    # Run each testcase
    total_score = 0.0
    max_score = 0.0
    testcase_results = []
    
    for testcase in testcases:
        max_score += testcase.points
        
        try:
            # Combine student code with testcase function and execution code
            # The testcase function should accept the student namespace/variables
            combined_test_code = f"""
# Student code
{student_code}

# Test function
{testcase.testcase_function}

# Execute test function
import json
try:
    # The test function should exist now
    result = {testcase.testcase_name}(globals())
    # Output result as JSON so we can parse it
    print("__TEST_RESULT__")
    print(json.dumps(result if isinstance(result, dict) else {{"score": 0.0, "feedback": "Invalid result format"}}))
except Exception as e:
    print("__TEST_RESULT__")
    print(json.dumps({{"score": 0.0, "feedback": f"Error: {{str(e)}}"}}))
"""
            
            # Use testcase timeout or provided timeout
            exec_timeout = timeout if timeout is not None else testcase.timeout
            
            test_config = ExecutionConfig(
                timeout=exec_timeout,
                memory_limit="256m",
                language=ExecutionLanguage.PYTHON
            )
            
            # Execute testcase with Docker
            # Pass empty student_code since it's already in combined_test_code
            test_result = await executor.execute(
                student_code="",  # Already included in combined_test_code
                test_code=combined_test_code,
                config_override=test_config
            )
            
            if not test_result.success:
                testcase_results.append({
                    "testcase_name": testcase.testcase_name,
                    "passed": False,
                    "score": 0.0,
                    "max_score": testcase.points,
                    "feedback": f"Test execution failed: {test_result.error_message or test_result.stderr}"
                })
                continue
            
            # Parse the JSON result from output
            import json
            output_lines = test_result.stdout.strip().split('\n')
            result_dict = None
            
            # Find the __TEST_RESULT__ marker and parse JSON
            for i, line in enumerate(output_lines):
                if line == "__TEST_RESULT__" and i + 1 < len(output_lines):
                    try:
                        result_dict = json.loads(output_lines[i + 1])
                        break
                    except json.JSONDecodeError:
                        pass
            
            if not result_dict:
                testcase_results.append({
                    "testcase_name": testcase.testcase_name,
                    "passed": False,
                    "score": 0.0,
                    "max_score": testcase.points,
                    "feedback": f"Could not parse test result"
                })
                continue
            
                continue
            
            # Parse result
            if isinstance(result_dict, dict):
                test_score = result_dict.get('score', 0.0)
                if isinstance(test_score, (int, float)):
                    # Normalize score to points
                    if 0 <= test_score <= 1:
                        # Score is a fraction
                        actual_score = test_score * testcase.points
                    else:
                        # Score is absolute
                        actual_score = min(test_score, testcase.points)
                else:
                    actual_score = 0.0
                
                feedback = result_dict.get('feedback', 'Test executed')
                passed = actual_score >= testcase.points * 0.5  # Pass if >= 50%
                
                testcase_results.append({
                    "testcase_name": testcase.testcase_name,
                    "passed": passed,
                    "score": actual_score,
                    "max_score": testcase.points,
                    "feedback": feedback
                })
                
                total_score += actual_score
            else:
                testcase_results.append({
                    "testcase_name": testcase.testcase_name,
                    "passed": False,
                    "score": 0.0,
                    "max_score": testcase.points,
                    "feedback": f"Invalid test result format. Expected dict with 'score' and 'feedback'"
                })
        
        except Exception as e:
            testcase_results.append({
                "testcase_name": testcase.testcase_name,
                "passed": False,
                "score": 0.0,
                "max_score": testcase.points,
                "feedback": f"Error executing testcase: {str(e)}"
            })
    
    # Calculate overall percentage
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Generate overall feedback
    passed_count = sum(1 for r in testcase_results if r['passed'])
    total_tests = len(testcase_results)
    
    overall_feedback = f"Passed {passed_count}/{total_tests} tests. Score: {total_score:.2f}/{max_score:.2f} ({percentage:.1f}%)"
    
    return {
        "success": True,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "passed_tests": passed_count,
        "total_tests": total_tests,
        "feedback": overall_feedback,
        "student_output": student_output,
        "results": testcase_results
    }
