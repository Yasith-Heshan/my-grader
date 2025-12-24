"""
Phase 2 Integration Tests
Test the Docker executor integration with grader_service
"""
import asyncio
import sys
from datetime import datetime

# Mock classes for testing without database
class MockTestCase:
    def __init__(self, test_code, points=10.0):
        self.test_code = test_code
        self.points = points

class MockSubmissionItem:
    def __init__(self, submitted_code):
        self.submitted_code = submitted_code

class MockSingleCellTestCase:
    def __init__(self, testcase_name, testcase_function, points=10.0, timeout=5):
        self.testcase_name = testcase_name
        self.testcase_function = testcase_function
        self.points = points
        self.timeout = timeout

# Import after mocks
from services.grader_service import grade_single_cell

async def test_basic_grading():
    """Test basic code grading with Docker executor"""
    print("\n" + "="*60)
    print("TEST 1: Basic Grading")
    print("="*60)
    
    # Create a simple test case
    test_case = MockTestCase(
        test_code="print('PASSED')",
        points=10.0
    )
    
    submission = MockSubmissionItem(
        submitted_code="x = 5\ny = 10\nresult = x + y"
    )
    
    try:
        result = await grade_single_cell(test_case, submission)
        
        print(f"✅ Test completed successfully!")
        print(f"   Passed: {result['passed']}")
        print(f"   Score: {result['score']}/{result['max_score']}")
        print(f"   Output: {result['output'][:100]}")
        print(f"   Feedback: {result['feedback'][:100]}")
        
        return result['passed']
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_math_operations():
    """Test math operations grading"""
    print("\n" + "="*60)
    print("TEST 2: Math Operations")
    print("="*60)
    
    test_case = MockTestCase(
        test_code="""
# Check if the result variable exists and equals 15
if 'result' in dir() and result == 15:
    print('PASSED')
else:
    print('FAILED: Expected result=15')
""",
        points=10.0
    )
    
    submission = MockSubmissionItem(
        submitted_code="""
x = 5
y = 10
result = x + y
"""
    )
    
    try:
        result = await grade_single_cell(test_case, submission)
        
        print(f"✅ Test completed!")
        print(f"   Passed: {result['passed']}")
        print(f"   Score: {result['score']}/{result['max_score']}")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling in student code"""
    print("\n" + "="*60)
    print("TEST 3: Error Handling")
    print("="*60)
    
    test_case = MockTestCase(
        test_code="print('PASSED')",
        points=10.0
    )
    
    submission = MockSubmissionItem(
        submitted_code="x = 1 / 0  # Division by zero error"
    )
    
    try:
        result = await grade_single_cell(test_case, submission)
        
        print(f"✅ Error handled correctly!")
        print(f"   Passed: {result['passed']}")
        print(f"   Score: {result['score']}/{result['max_score']}")
        print(f"   Feedback snippet: {result['feedback'][:150]}")
        
        # Should not pass when there's an error
        return not result['passed']
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_docker_executor_availability():
    """Test that Docker executor is available"""
    print("\n" + "="*60)
    print("TEST 4: Docker Executor Availability")
    print("="*60)
    
    try:
        from utils.executor_factory import ExecutorFactory
        from utils.executor_interface import ExecutionConfig, ExecutionLanguage
        
        executor = await ExecutorFactory.get_default_executor()
        print(f"✅ Executor created: {type(executor).__name__}")
        
        # Try a simple execution
        config = ExecutionConfig(
            timeout=5,
            memory_limit="128m",
            language=ExecutionLanguage.PYTHON
        )
        
        result = await executor.execute(
            student_code="print('Hello from Docker!')",
            test_code="# Test code",
            config_override=config
        )
        
        print(f"✅ Execution successful!")
        print(f"   Success: {result.success}")
        print(f"   Output: {result.stdout}")
        
        return result.success
    except Exception as e:
        print(f"❌ Docker executor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "╔" + "="*60 + "╗")
    print("║" + " "*10 + "PHASE 2 INTEGRATION TESTS" + " "*25 + "║")
    print("╚" + "="*60 + "╝")
    
    tests = [
        ("Docker Executor Availability", test_docker_executor_availability),
        ("Basic Grading", test_basic_grading),
        ("Math Operations", test_math_operations),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = await test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Phase 2 integration successful!")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
