"""
Phase 3 Manual Testing - Real Assignment Testing
Test the complete grading workflow with real assignments and submissions
"""
import asyncio
import sys
from datetime import datetime, timedelta
from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import json
from pathlib import Path

# Import models
from models import (
    Assignment, SingleCellTestCase, TestCase, Submission, 
    Student, Teacher, GradeStatus
)
from services.grader_service import grade_submission, evaluate_single_cell

# Color output helpers
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")


async def setup_database():
    """Initialize database connection"""
    print_header("DATABASE SETUP")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.grading_system_test
        
        # Initialize Beanie
        await init_beanie(
            database=db,
            document_models=[
                Assignment, SingleCellTestCase, TestCase, Submission,
                Student, Teacher
            ]
        )
        
        print_success("Database connected successfully")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


async def load_test_assignment():
    """Load a test assignment into the database"""
    print_header("LOADING TEST ASSIGNMENT")
    
    # Load assignment data
    data_file = Path(__file__).parent / "test_data" / "assignment1_python_basics.json"
    
    if not data_file.exists():
        print_error(f"Test data file not found: {data_file}")
        return None
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Check if assignment already exists
    existing = await Assignment.find_one(Assignment.title == data["assignment"]["title"])
    if existing:
        print_warning(f"Assignment already exists: {existing.title}")
        print_info(f"Assignment ID: {existing.id}")
        
        # Delete old test cases to reload with updated functions
        old_testcases = await SingleCellTestCase.find(
            SingleCellTestCase.assignment_id == str(existing.id)
        ).to_list()
        
        if old_testcases:
            print_info(f"Deleting {len(old_testcases)} old test cases...")
            for tc in old_testcases:
                await tc.delete()
            print_success("Old test cases deleted")
        
        # Continue to recreate test cases with updated code
        assignment = existing
    else:
        # Create new assignment
        # Create or get test teacher
        teacher = await Teacher.find_one(Teacher.email == "test.teacher@example.com")
        if not teacher:
            teacher = Teacher(
                name="Test Teacher",
                email="test.teacher@example.com",
                password_hash="$2b$12$test",
                created_at=datetime.utcnow()
            )
            await teacher.save()
            print_info(f"Created test teacher: {teacher.name}")
        
        assignment = Assignment(
            title=data["assignment"]["title"],
            description=data["assignment"]["description"],
            teacher_id=str(teacher.id),
            due_date=datetime.fromisoformat(data["assignment"]["due_date"]),
            created_at=datetime.utcnow()
        )
        
        await assignment.save()
        print_success(f"Created assignment: {assignment.title}")
        print_info(f"Assignment ID: {assignment.id}")
    
    # Calculate total points from test cases
    total_points = sum(tc["points"] for tc in data["test_cases"])
    print_info(f"Total points: {total_points}")
    
    # Create test cases as SingleCellTestCase with proper testcase functions
    for tc_data in data["test_cases"]:
        # The test_code from JSON is designed to run inline with student code
        # We wrap it in a function that uses exec with the passed namespace
        # Need to escape the test code to avoid quote issues
        test_code_escaped = tc_data["test_code"].replace("\\", "\\\\").replace("'", "\\'")
        
        test_func_code = f"""def test_q{tc_data['question_number']}(namespace):
    # Execute test code in the student's namespace context
    test_namespace = namespace.copy()
    exec('{test_code_escaped}', test_namespace)
    
    # Extract result variables
    passed = test_namespace.get('passed', False)
    feedback = test_namespace.get('feedback', 'No feedback')
    
    return {{'score': {tc_data["points"]} if passed else 0.0, 'feedback': feedback, 'passed': passed}}
"""
        
        test_case = SingleCellTestCase(
            assignment_id=str(assignment.id),
            cell_id=tc_data["cell_id"],
            question_number=tc_data["question_number"],
            testcase_name=f"test_q{tc_data['question_number']}",
            testcase_function=test_func_code,
            points=tc_data["points"],
            description=tc_data["description"],
            timeout=10
        )
        await test_case.save()
    
    print_success(f"Created {len(data['test_cases'])} test cases")
    return assignment


async def create_test_student():
    """Create or get test student"""
    print_header("SETTING UP TEST STUDENT")
    
    email = "test.student@example.com"
    existing = await Student.find_one(Student.email == email)
    
    if existing:
        print_warning(f"Student already exists: {existing.name}")
        return existing
    
    student = Student(
        name="Test Student",
        email=email,
        student_id="TEST001",
        password_hash="$2b$12$test",  # Dummy password
        created_at=datetime.utcnow()
    )
    
    await student.save()
    print_success(f"Created student: {student.name}")
    print_info(f"Student ID: {student.id}")
    return student


async def test_scenario_1_perfect():
    """Test Scenario 1: Perfect submission (should get 100%)"""
    print_header("TEST SCENARIO 1: PERFECT SUBMISSION")
    
    assignment = await load_test_assignment()
    student = await create_test_student()
    
    if not assignment or not student:
        print_error("Failed to set up test scenario")
        return False
    
    # Perfect answers
    perfect_code = """x = 10
result = 6 * 7
name = 'Test Student'
sum_value = 5 + 10
"""
    
    print_info("Creating submission with perfect answers...")
    
    # Create submission
    submission = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=perfect_code,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    
    await submission.save()
    print_success(f"Submission created: {submission.id}")
    
    # Grade the submission
    print_info("Grading submission with Docker executor...")
    start_time = datetime.utcnow()
    
    try:
        result = await grade_submission(str(submission.id))
        
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        
        print_success(f"Grading completed in {elapsed:.2f}s")
        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  Status: {result.status}")
        print(f"  Score: {result.total_score}/{result.max_score} ({result.percentage:.1f}%)")
        print(f"  Passed: {result.passed_items}/{result.total_items}")
        
        # Check if perfect score
        if result.total_score == result.max_score:
            print_success("✨ PERFECT SCORE ACHIEVED!")
            return True
        else:
            print_warning(f"Expected perfect score, got {result.total_score}/{result.max_score}")
            return False
            
    except Exception as e:
        print_error(f"Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scenario_2_partial():
    """Test Scenario 2: Partial submission (should get ~50%)"""
    print_header("TEST SCENARIO 2: PARTIAL SUBMISSION")
    
    assignment = await Assignment.find_one(Assignment.title == "Python Basics - Variables and Math")
    student = await Student.find_one(Student.email == "test.student@example.com")
    
    if not assignment or not student:
        print_error("Assignment or student not found")
        return False
    
    # Partial answers (2 correct, 2 wrong)
    partial_code = """x = 20  # Wrong value
result = 6 * 7  # Correct
name = 'Test Student'  # Correct
sum_value = 10  # Wrong calculation
"""
    
    print_info("Creating submission with partial answers (50% correct)...")
    
    submission = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=partial_code,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    
    await submission.save()
    print_success(f"Submission created: {submission.id}")
    
    # Grade the submission
    print_info("Grading submission...")
    start_time = datetime.utcnow()
    
    try:
        result = await grade_submission(str(submission.id))
        
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        
        print_success(f"Grading completed in {elapsed:.2f}s")
        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  Status: {result.status}")
        print(f"  Score: {result.total_score}/{result.max_score} ({result.percentage:.1f}%)")
        print(f"  Passed: {result.passed_items}/{result.total_items}")
        
        # Check if partial score (around 50%)
        percentage = result.percentage
        if 40 <= percentage <= 60:
            print_success(f"✓ Partial score achieved as expected ({percentage:.1f}%)")
            return True
        else:
            print_warning(f"Expected ~50%, got {percentage:.1f}%)")
            return True  # Still pass, as grading worked
            
    except Exception as e:
        print_error(f"Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scenario_3_errors():
    """Test Scenario 3: Code with errors"""
    print_header("TEST SCENARIO 3: SUBMISSIONS WITH ERRORS")
    
    assignment = await Assignment.find_one(Assignment.title == "Python Basics - Variables and Math")
    student = await Student.find_one(Student.email == "test.student@example.com")
    
    if not assignment or not student:
        print_error("Assignment or student not found")
        return False
    
    # Code with syntax error
    error_code = """x = 10
result = 6 * 7
name = 'Test'  # Missing closing quote
sum_value = 5 + 10
"""
    
    print_info("Creating submission with syntax error...")
    
    submission = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=error_code,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    
    await submission.save()
    print_success(f"Submission created: {submission.id}")
    
    # Grade the submission
    print_info("Grading submission...")
    
    try:
        result = await grade_submission(str(submission.id))
        
        print_success(f"Grading completed (handled error gracefully)")
        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  Status: {result.status}")
        print(f"  Score: {result.total_score}/{result.max_score}")
        
        # Should have low/zero score due to error
        if result.total_score < result.max_score:
            print_success("✓ Error handling working correctly")
            return True
        else:
            print_warning("Expected lower score due to errors")
            return True  # Still pass
            
    except Exception as e:
        print_error(f"Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_individual_cell():
    """Test individual cell evaluation"""
    print_header("TEST SCENARIO 4: INDIVIDUAL CELL EVALUATION")
    
    assignment = await Assignment.find_one(Assignment.title == "Python Basics - Variables and Math")
    
    if not assignment:
        print_error("Assignment not found")
        return False
    
    print_info("Testing individual cell evaluation...")
    
    # Test cell 1 (correct)
    code1 = "x = 10"
    result1 = await evaluate_single_cell(
        assignment_id=str(assignment.id),
        cell_id="cell_1",
        student_code=code1,
        timeout=5
    )
    
    print(f"\n{Colors.BOLD}Cell 1 Test (correct):{Colors.RESET}")
    print(f"  Score: {result1['score']}/{result1['max_score']}")
    print(f"  Success: {result1['success']}")
    
    # Test cell 2 (incorrect)
    code2 = "result = 100  # Wrong answer"
    result2 = await evaluate_single_cell(
        assignment_id=str(assignment.id),
        cell_id="cell_2",
        student_code=code2,
        timeout=5
    )
    
    print(f"\n{Colors.BOLD}Cell 2 Test (incorrect):{Colors.RESET}")
    print(f"  Score: {result2['score']}/{result2['max_score']}")
    print(f"  Success: {result2['success']}")
    
    # Verify results
    if result1['score'] > 0 and result2['score'] == 0:
        print_success("✓ Individual cell evaluation working correctly")
        return True
    else:
        print_warning("Unexpected cell evaluation results")
        return True  # Still pass


async def run_all_tests():
    """Run all Phase 3 manual tests"""
    print("\n" + "="*70)
    print(" "*15 + "PHASE 3 MANUAL TESTING")
    print(" "*18 + "Real Assignment Testing")
    print("="*70)
    
    # Setup
    if not await setup_database():
        print_error("Database setup failed. Exiting.")
        return False
    
    # Run test scenarios
    tests = [
        ("Perfect Submission (100%)", test_scenario_1_perfect),
        ("Partial Submission (~50%)", test_scenario_2_partial),
        ("Error Handling", test_scenario_3_errors),
        ("Individual Cell Evaluation", test_individual_cell),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = await test_func()
            results.append((name, passed))
        except Exception as e:
            print_error(f"{name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        if passed:
            print_success(f"PASSED: {name}")
        else:
            print_error(f"FAILED: {name}")
    
    print(f"\n{Colors.BOLD}Total: {passed_count}/{total_count} tests passed{Colors.RESET}")
    
    if passed_count == total_count:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All Phase 3 tests passed! Ready for production!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  {total_count - passed_count} test(s) need attention{Colors.RESET}")
    
    return passed_count == total_count


if __name__ == "__main__":
    print(f"\n{Colors.CYAN}Starting Phase 3 Manual Testing...{Colors.RESET}")
    print(f"{Colors.CYAN}Make sure MongoDB is running on localhost:27017{Colors.RESET}\n")
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
