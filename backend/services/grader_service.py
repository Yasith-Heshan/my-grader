"""
Grader service - Business logic for grading operations using Docker executor
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId
import json

from models import Submission, SubmissionItem, TestCase, GradeStatus, Student, Assignment, SingleCellTestCase
from schemas import GradingResult, SubmissionItemResponse, StudentResult, AssignmentSummary
from utils.executor_factory import ExecutorFactory
from utils.executor_interface import ExecutionConfig, ExecutionLanguage

async def grade_single_cell(test_case: TestCase, submission_item: SubmissionItem) -> Dict[str, Any]:
    """Grade a single cell submission against a test case using Docker executor"""
    try:
        executor = await ExecutorFactory.get_default_executor()
        config = ExecutionConfig(
            timeout=10,
            memory_limit="256m",
            language=ExecutionLanguage.PYTHON
        )
        
        # Execute student code with test code in Docker
        result = await executor.execute(
            student_code=submission_item.submitted_code,
            test_code=test_case.test_code,
            config_override=config
        )
        
        if not result.success:
            return {
                'passed': False,
                'score': 0.0,
                'max_score': test_case.points,
                'output': result.stdout,
                'feedback': f'Execution error: {result.error_message or result.stderr}'
            }
        
        # Parse result - test_code should set 'passed' and 'feedback' variables
        output = result.stdout
        passed = 'PASSED' in output.upper() or result.return_value == True
        score = test_case.points if passed else 0.0
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
            'feedback': f'Error: {str(e)}'
        }

async def grade_submission(submission_id: str) -> GradingResult:
    """Grade a full submission by evaluating code against test cases"""
    submission = await Submission.get(PydanticObjectId(submission_id))
    
    if not submission:
        raise ValueError(f"Submission {submission_id} not found")
    
    # Update status to grading
    submission.status = GradeStatus.GRADING
    await submission.save()
    
    # Single-code submission path
    if submission.code:
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
        
        submission.total_score = total_score
        submission.max_score = max_score
        submission.status = GradeStatus.COMPLETED
        submission.graded_at = datetime.utcnow()
        await submission.save()
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed_tests = 1 if total_score >= max_score * 0.7 else 0
        
        return GradingResult(
            submission_id=str(submission.id),
            status="completed",
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            passed_items=passed_tests,
            total_items=1,
            items=[],
            message=f"Score: {total_score:.1f}/{max_score:.1f} ({percentage:.1f}%)"
        )
    
    # Multi-cell submission path
    items = await SubmissionItem.find(
        SubmissionItem.submission_id == str(submission.id)
    ).to_list()
    
    total_score = 0.0
    max_score = 0.0
    passed_count = 0
    
    for item in items:
        test_case = await TestCase.get(PydanticObjectId(item.test_case_id))
        if not test_case:
            continue
        
        result = await grade_single_cell(test_case, item)
        
        item.passed = result['passed']
        item.score = result['score']
        item.max_score = result['max_score']
        item.output = result['output']
        item.feedback = result['feedback']
        item.graded_at = datetime.utcnow()
        await item.save()
        
        total_score += result['score']
        max_score += result['max_score']
        passed_count += 1 if result['passed'] else 0
    
    submission.total_score = total_score
    submission.max_score = max_score
    submission.status = GradeStatus.COMPLETED
    submission.graded_at = datetime.utcnow()
    await submission.save()
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    item_responses = [
        SubmissionItemResponse(**{**item.model_dump(), '_id': str(item.id)})
        for item in items
    ]
    
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
    
    items = await SubmissionItem.find(SubmissionItem.submission_id == str(submission.id)).to_list()
    passed_count = sum(1 for item in items if item.passed)
    percentage = (submission.total_score / submission.max_score * 100) if submission.max_score > 0 else 0
    
    item_responses = [
        SubmissionItemResponse(**{**item.model_dump(), '_id': str(item.id)})
        for item in items
    ]
    
    return GradingResult(
        submission_id=str(submission.id),
        status=submission.status.value,
        total_score=submission.total_score,
        max_score=submission.max_score,
        percentage=percentage,
        passed_items=passed_count,
        total_items=len(items),
        items=item_responses,
        message=f"Submission {submission.status.value}"
    )


async def get_student_submission(assignment_id: str, student_id: str) -> Optional[Submission]:
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
    
    submissions = await Submission.find(Submission.assignment_id == assignment_id).to_list()
    
    total_submissions = len(submissions)
    graded_submissions = sum(1 for s in submissions if s.status == GradeStatus.COMPLETED)
    pending_submissions = sum(1 for s in submissions if s.status == GradeStatus.PENDING)
    
    completed = [s for s in submissions if s.status == GradeStatus.COMPLETED and s.max_score > 0]
    average_score = sum(s.total_score / s.max_score * 100 for s in completed) / len(completed) if completed else 0.0
    
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


# Single-Cell Evaluation with Docker Executor

async def evaluate_single_cell(
    assignment_id: str,
    cell_id: str,
    student_code: str,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluate student code against test cases using Docker executor
    
    Args:
        assignment_id: Assignment ID
        cell_id: Cell identifier  
        student_code: Student's submitted code
        timeout: Optional timeout override
        
    Returns:
        Dict with score, feedback, and test results
    """
    testcases = await SingleCellTestCase.find(
        SingleCellTestCase.assignment_id == assignment_id,
        SingleCellTestCase.cell_id == cell_id
    ).to_list()
    
    if not testcases:
        return {
            "success": False,
            "score": 0.0,
            "max_score": 0.0,
            "feedback": f"No test cases found for cell '{cell_id}'",
            "results": []
        }
    
    executor = await ExecutorFactory.get_default_executor()
    config = ExecutionConfig(
        timeout=timeout or 10,
        memory_limit="256m",
        language=ExecutionLanguage.PYTHON
    )
    
    # Execute student code first
    student_result = await executor.execute(
        student_code=student_code,
        test_code="# Student code executed",
        config_override=config
    )
    
    if not student_result.success:
        return {
            "success": False,
            "score": 0.0,
            "max_score": sum(tc.points for tc in testcases),
            "feedback": f"Error: {student_result.error_message or student_result.stderr}",
            "student_output": student_result.stdout,
            "results": []
        }
    
    # Run each test case
    total_score = 0.0
    max_score = 0.0
    testcase_results = []
    
    for testcase in testcases:
        max_score += testcase.points
        
        try:
            # Combine student code with test function
            combined_code = f"""
{student_code}

{testcase.testcase_function}

import json
try:
    result = {testcase.testcase_name}(globals())
    print("__TEST_RESULT__")
    print(json.dumps(result if isinstance(result, dict) else {{"score": 0.0, "feedback": "Invalid format"}}))
except Exception as e:
    print("__TEST_RESULT__")
    print(json.dumps({{"score": 0.0, "feedback": f"Error: {{str(e)}}"}}))
"""
            
            test_config = ExecutionConfig(
                timeout=timeout or testcase.timeout,
                memory_limit="256m",
                language=ExecutionLanguage.PYTHON
            )
            
            test_result = await executor.execute(
                student_code="",
                test_code=combined_code,
                config_override=test_config
            )
            
            if not test_result.success:
                testcase_results.append({
                    "testcase_name": testcase.testcase_name,
                    "passed": False,
                    "score": 0.0,
                    "max_score": testcase.points,
                    "feedback": f"Execution failed: {test_result.error_message or test_result.stderr}"
                })
                continue
            
            # Parse JSON result from output
            output_lines = test_result.stdout.strip().split('\n')
            result_dict = None
            
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
                    "feedback": "Could not parse test result"
                })
                continue
            
            # Calculate score
            test_score = result_dict.get('score', 0.0)
            if isinstance(test_score, (int, float)):
                if 0 <= test_score <= 1:
                    actual_score = test_score * testcase.points  # Fraction
                else:
                    actual_score = min(test_score, testcase.points)  # Absolute
            else:
                actual_score = 0.0
            
            feedback = result_dict.get('feedback', 'Test executed')
            passed = actual_score >= testcase.points * 0.5
            
            testcase_results.append({
                "testcase_name": testcase.testcase_name,
                "passed": passed,
                "score": actual_score,
                "max_score": testcase.points,
                "feedback": feedback
            })
            
            total_score += actual_score
        
        except Exception as e:
            testcase_results.append({
                "testcase_name": testcase.testcase_name,
                "passed": False,
                "score": 0.0,
                "max_score": testcase.points,
                "feedback": f"Error: {str(e)}"
            })
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    passed_count = sum(1 for r in testcase_results if r['passed'])
    
    return {
        "success": True,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "passed_tests": passed_count,
        "total_tests": len(testcase_results),
        "feedback": f"Passed {passed_count}/{len(testcase_results)} tests. Score: {total_score:.2f}/{max_score:.2f}",
        "student_output": student_result.stdout,
        "results": testcase_results
    }
