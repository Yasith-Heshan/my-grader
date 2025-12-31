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

from models import (
    Submission,
    SubmissionItem,
    TestCase,
    GradeStatus,
    Student,
    Assignment,
    SingleCellTestCase,
)
from schemas import (
    GradingResult,
    SubmissionItemResponse,
    StudentResult,
    AssignmentSummary,
)


def grade_single_cell(
    test_case: TestCase, submission_item: SubmissionItem
) -> Dict[str, Any]:
    """
    Grade a single cell submission against a test case.
    This is a placeholder implementation that executes the student code
    and the test code to verify correctness.
    """
    try:
        # Create a namespace for code execution
        namespace = {}

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Execute student's submitted code
        exec(submission_item.submitted_code, namespace)

        # Execute test code in the same namespace
        exec(test_case.test_code, namespace)

        # Get the output
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Check if test passed (test_code should set 'passed' variable)
        passed = namespace.get("passed", False)

        # Calculate score
        score = test_case.points if passed else 0.0

        # Generate feedback
        feedback = namespace.get(
            "feedback", "Test executed successfully" if passed else "Test failed"
        )

        return {
            "passed": passed,
            "score": score,
            "max_score": test_case.points,
            "output": output,
            "feedback": feedback,
        }

    except Exception as e:
        # Restore stdout
        sys.stdout = old_stdout

        return {
            "passed": False,
            "score": 0.0,
            "max_score": test_case.points,
            "output": "",
            "feedback": f"Error executing code: {str(e)}\n{traceback.format_exc()}",
        }


async def grade_submission(submission_id: str) -> GradingResult:
    """Grade a full submission by evaluating code against test cases"""
    submission = await Submission.get(PydanticObjectId(submission_id))
    print("Submission code:", submission.code, submission)

    if not submission:
        raise ValueError(f"Submission {submission_id} not found")

    # Update status to grading
    submission.status = GradeStatus.GRADING
    await submission.save()

    # Check if submission has answers (multi-cell submission)
    if submission.answers:
        # Get all test cases for this assignment
        testcases = await SingleCellTestCase.find(
            SingleCellTestCase.assignment_id == submission.assignment_id
        ).to_list()
        print(testcases, "testcases")
        if not testcases:
            submission.status = GradeStatus.COMPLETED
            submission.total_score = 0.0
            submission.max_score = 0.0
            submission.graded_at = datetime.utcnow()
            await submission.save()
            raise ValueError(
                f"No test cases found for assignment {submission.assignment_id}"
            )

        # Create a map of cell_id to student code
        answers_map = {answer.cell_id: answer.code for answer in submission.answers}

        # Evaluate against each test case
        total_score = 0.0
        max_score = 0.0

        for testcase in testcases:
            # Get the student code for this cell
            student_code = answers_map.get(testcase.cell_id, "")

            if not student_code:
                print(f"Warning: No student code found for cell {testcase.cell_id}")
                max_score += testcase.points
                continue

            result = await evaluate_single_cell(
                assignment_id=submission.assignment_id,
                cell_id=testcase.cell_id,
                student_code=student_code,
                timeout=testcase.timeout,
            )
            print("\n", result, "result\n")

            total_score += result.get("score", 0.0)
            max_score += result.get("max_score", 0.0)

        # Update submission with scores
        submission.total_score = total_score
        submission.max_score = max_score
        submission.status = GradeStatus.COMPLETED
        submission.graded_at = datetime.utcnow()
        await submission.save()
        print("Submission after grading:", submission)

        return GradingResult(
            submission_id=str(submission.id),
            total_score=total_score,
            max_score=max_score,
            passed_count=1 if total_score >= max_score * 0.7 else 0,
            failed_count=0 if total_score >= max_score * 0.7 else 1,
            items=[],
            # submission_id=str(submission.id),
            status=submission.status.value,
            # total_score=total_score,
            # max_score=max_score,
            percentage=100,
            passed_items=1,
            total_items=0,
            message=f"Graded single-cell submission. Score: {total_score}/{max_score}",
            # items=item_responses,
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

        # Grade the item
        result = grade_single_cell(test_case, item)

        # Update submission item with results
        item.passed = result["passed"]
        item.score = result["score"]
        item.max_score = result["max_score"]
        item.output = result["output"]
        item.feedback = result["feedback"]
        item.graded_at = datetime.utcnow()
        await item.save()

        # Accumulate totals
        total_score += result["score"]
        max_score += result["max_score"]
        passed_count += 1 if result["passed"] else 0

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
        item_dict["_id"] = str(item.id)
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
        message=f"Graded {len(items)} items. Score: {total_score}/{max_score} ({percentage:.1f}%)",
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
            results.append(
                {
                    "submission_id": str(submission.id),
                    "student_id": submission.student_id,
                    "status": "completed",
                    "score": result.total_score,
                    "max_score": result.max_score,
                }
            )
        except Exception as e:
            submission.status = GradeStatus.FAILED
            await submission.save()
            results.append(
                {
                    "submission_id": str(submission.id),
                    "student_id": submission.student_id,
                    "status": "failed",
                    "error": str(e),
                }
            )

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
    percentage = (
        (submission.total_score / submission.max_score * 100)
        if submission.max_score > 0
        else 0
    )

    # Convert items to response format
    item_responses = []
    for item in items:
        item_dict = item.model_dump()
        item_dict["_id"] = str(item.id)
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
        message=f"Submission grading {submission.status.value}",
    )


async def get_student_submission(
    assignment_id: str, student_id: str
) -> Optional[Submission]:
    """Get a student's submission for an assignment"""
    return await Submission.find_one(
        Submission.assignment_id == assignment_id, Submission.student_id == student_id
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
    graded_submissions = sum(
        1 for s in submissions if s.status == GradeStatus.COMPLETED
    )
    pending_submissions = sum(1 for s in submissions if s.status == GradeStatus.PENDING)

    # Calculate average score
    completed = [
        s for s in submissions if s.status == GradeStatus.COMPLETED and s.max_score > 0
    ]
    average_score = (
        sum(s.total_score / s.max_score * 100 for s in completed) / len(completed)
        if completed
        else 0.0
    )

    # Prepare student results
    student_results = []
    for submission in submissions:
        student = await Student.get(PydanticObjectId(submission.student_id))
        percentage = (
            (submission.total_score / submission.max_score * 100)
            if submission.max_score > 0
            else 0
        )

        student_results.append(
            StudentResult(
                student_id=str(submission.student_id),
                student_name=student.name if student else "Unknown",
                total_score=submission.total_score,
                max_score=submission.max_score,
                percentage=percentage,
                status=submission.status.value,
                submitted_at=submission.submitted_at,
                graded_at=submission.graded_at,
            )
        )

    return AssignmentSummary(
        assignment_id=str(assignment.id),
        assignment_title=assignment.title,
        total_submissions=total_submissions,
        graded_submissions=graded_submissions,
        pending_submissions=pending_submissions,
        average_score=average_score,
        students=student_results,
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
    if hasattr(signal, "SIGALRM"):
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
    assignment_id: str, cell_id: str, student_code: str, timeout: Optional[int] = None
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
        SingleCellTestCase.cell_id == cell_id,
    ).to_list()

    if not testcases:
        return {
            "success": False,
            "score": 0.0,
            "max_score": 0.0,
            "feedback": f"No testcases found for cell '{cell_id}'",
            "results": [],
        }

    # Execute student code and collect namespace
    student_namespace = {}
    student_output = ""
    student_error = None

    try:
        # Capture stdout during student code execution
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Execute student code
        exec(student_code, student_namespace)

        # Get captured output
        student_output = sys.stdout.getvalue()
        sys.stdout = old_stdout

    except Exception as e:
        sys.stdout = old_stdout
        student_error = f"Error in student code: {str(e)}\n{traceback.format_exc()}"

        return {
            "success": False,
            "score": 0.0,
            "max_score": sum(tc.points for tc in testcases),
            "feedback": student_error,
            "student_output": student_output,
            "results": [],
        }

    # Run each testcase
    total_score = 0.0
    max_score = 0.0
    testcase_results = []

    for testcase in testcases:
        max_score += testcase.points

        try:
            # Create namespace for testcase execution
            testcase_namespace = {
                "submission": student_namespace,
                "math": __import__("math"),
                "json": __import__("json"),
                "datetime": __import__("datetime"),
            }

            # Use testcase timeout or provided timeout
            exec_timeout = timeout if timeout is not None else testcase.timeout

            # Execute testcase function
            exec(testcase.testcase_function, testcase_namespace)

            # Find the test function (should match testcase_name)
            test_func = testcase_namespace.get(testcase.testcase_name)

            if not test_func:
                # Try to find any function that's not a builtin
                for name, obj in testcase_namespace.items():
                    if (
                        callable(obj)
                        and not name.startswith("_")
                        and name not in ["math", "json", "datetime", "submission"]
                    ):
                        test_func = obj
                        break

            if not test_func or not callable(test_func):
                testcase_results.append(
                    {
                        "testcase_name": testcase.testcase_name,
                        "passed": False,
                        "score": 0.0,
                        "max_score": testcase.points,
                        "feedback": f"Testcase function '{testcase.testcase_name}' not found",
                    }
                )
                continue

            # Execute the test function with timeout
            try:
                with time_limit(exec_timeout):
                    result = test_func(student_namespace)
            except TimeoutException:
                testcase_results.append(
                    {
                        "testcase_name": testcase.testcase_name,
                        "passed": False,
                        "score": 0.0,
                        "max_score": testcase.points,
                        "feedback": f"Test execution timed out (>{exec_timeout}s)",
                    }
                )
                continue

            # Parse result
            if isinstance(result, dict):
                test_score = result.get("score", 0.0)
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

                feedback = result.get("feedback", "Test executed")
                passed = actual_score >= testcase.points * 0.5  # Pass if >= 50%

                testcase_results.append(
                    {
                        "testcase_name": testcase.testcase_name,
                        "passed": passed,
                        "score": actual_score,
                        "max_score": testcase.points,
                        "feedback": feedback,
                    }
                )

                total_score += actual_score
            else:
                testcase_results.append(
                    {
                        "testcase_name": testcase.testcase_name,
                        "passed": False,
                        "score": 0.0,
                        "max_score": testcase.points,
                        "feedback": f"Invalid test result format. Expected dict with 'score' and 'feedback'",
                    }
                )

        except Exception as e:
            testcase_results.append(
                {
                    "testcase_name": testcase.testcase_name,
                    "passed": False,
                    "score": 0.0,
                    "max_score": testcase.points,
                    "feedback": f"Error executing testcase: {str(e)}",
                }
            )

    # Calculate overall percentage
    percentage = (total_score / max_score * 100) if max_score > 0 else 0

    # Generate overall feedback
    passed_count = sum(1 for r in testcase_results if r["passed"])
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
        "results": testcase_results,
    }
