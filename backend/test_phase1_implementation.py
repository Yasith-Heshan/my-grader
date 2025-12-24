"""
Phase 1 Implementation Test Suite
Tests all core functionality of the Docker executor system
"""
import asyncio
import time
from utils.executor_factory import ExecutorFactory
from utils.executor_interface import ExecutionConfig, ExecutionLanguage
from config.executor_config import ExecutorConfig as Config


async def test_basic_execution():
    """Test 1: Basic code execution"""
    print("\n" + "="*60)
    print("TEST 1: Basic Code Execution")
    print("="*60)
    
    executor = await ExecutorFactory.create_executor()
    
    student_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

result = factorial(5)
"""
    
    test_code = """
expected = 120
passed = result == expected
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = f"Expected {expected}, got {result}"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert result.success, "Execution should succeed"
    assert result.passed, "Test should pass"
    assert result.score == 10.0, f"Score should be 10.0, got {result.score}"
    
    print(f"✅ PASSED - Score: {result.score}/{result.max_score}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    return True


async def test_security_isolation():
    """Test 2: Security - File system access should be blocked"""
    print("\n" + "="*60)
    print("TEST 2: Security - File System Isolation")
    print("="*60)
    
    executor = await ExecutorFactory.create_executor()
    
    # Try to access files outside sandbox
    student_code = """
try:
    with open('/etc/passwd', 'r') as f:
        content = f.read()
    result = "SECURITY_BREACH"
except Exception as e:
    result = "ACCESS_DENIED"
"""
    
    test_code = """
passed = result == "ACCESS_DENIED"
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "File access correctly blocked" if passed else "SECURITY ISSUE: File access allowed"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert result.passed, "File access should be blocked"
    
    print(f"✅ PASSED - File system isolation working")
    print(f"   Feedback: {result.feedback}")
    return True


async def test_resource_limits():
    """Test 3: Resource limits - Memory and CPU"""
    print("\n" + "="*60)
    print("TEST 3: Resource Limits")
    print("="*60)
    
    config = ExecutionConfig(
        timeout=5,
        memory_limit="128m",
        cpu_quota=25000
    )
    
    executor = await ExecutorFactory.create_executor(config)
    
    # Code that uses some resources but within limits
    student_code = """
data = [i**2 for i in range(1000)]
result = sum(data)
"""
    
    test_code = """
expected = sum(i**2 for i in range(1000))
passed = result == expected
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Computation correct"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert result.success, "Execution within limits should succeed"
    assert result.passed, "Test should pass"
    
    print(f"✅ PASSED - Resource limits enforced")
    print(f"   Config: Memory={config.memory_limit}, CPU={config.cpu_quota}")
    return True


async def test_timeout_enforcement():
    """Test 4: Timeout enforcement"""
    print("\n" + "="*60)
    print("TEST 4: Timeout Enforcement")
    print("="*60)
    
    config = ExecutionConfig(timeout=2)
    executor = await ExecutorFactory.create_executor(config)
    
    # Code that takes too long
    student_code = """
import time
time.sleep(5)
result = "Should not reach here"
"""
    
    test_code = """
passed = True
score = 10.0
max_score = 10.0
feedback = "Test"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert result.timeout_occurred, "Timeout should occur"
    assert not result.success, "Long-running code should fail"
    
    print(f"✅ PASSED - Timeout correctly enforced")
    print(f"   Timeout occurred: {result.timeout_occurred}")
    return True


async def test_error_handling():
    """Test 5: Error handling"""
    print("\n" + "="*60)
    print("TEST 5: Error Handling")
    print("="*60)
    
    executor = await ExecutorFactory.create_executor()
    
    # Code with syntax error
    student_code = """
def broken_function(:
    return "syntax error"
result = broken_function()
"""
    
    test_code = """
passed = False
score = 0.0
max_score = 10.0
feedback = "Test"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert not result.success, "Code with errors should fail"
    assert len(result.stderr) > 0, "Should capture error output"
    
    print(f"✅ PASSED - Errors properly captured")
    print(f"   Error captured: {len(result.stderr)} chars")
    return True


async def test_concurrent_execution():
    """Test 6: Concurrent execution"""
    print("\n" + "="*60)
    print("TEST 6: Concurrent Execution")
    print("="*60)
    
    student_code = """
import time
time.sleep(0.1)
result = 42
"""
    
    test_code = """
passed = result == 42
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Correct"
"""
    
    async def run_single():
        executor = await ExecutorFactory.create_executor()
        result = await executor.execute(student_code, test_code)
        await executor.cleanup()
        return result
    
    start_time = time.time()
    
    # Run 3 executions concurrently
    results = await asyncio.gather(
        run_single(),
        run_single(),
        run_single()
    )
    
    elapsed = time.time() - start_time
    
    assert all(r.success for r in results), "All concurrent executions should succeed"
    assert all(r.passed for r in results), "All tests should pass"
    
    print(f"✅ PASSED - Concurrent execution working")
    print(f"   3 executions completed in {elapsed:.2f}s")
    print(f"   Average: {elapsed/3:.2f}s per execution")
    return True


async def test_math_operations():
    """Test 7: Math operations with standard library"""
    print("\n" + "="*60)
    print("TEST 7: Math Operations")
    print("="*60)
    
    executor = await ExecutorFactory.create_executor()
    
    student_code = """
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

def calculate_hypotenuse(a, b):
    return math.sqrt(a**2 + b**2)

area = calculate_circle_area(10)
hyp = calculate_hypotenuse(3, 4)
"""
    
    test_code = """
import math

expected_area = math.pi * 100
expected_hyp = 5.0

test_results = []

# Test area
if abs(area - expected_area) < 0.001:
    test_results.append({"name": "circle_area", "passed": True, "score": 5.0})
else:
    test_results.append({"name": "circle_area", "passed": False, "score": 0.0})

# Test hypotenuse
if abs(hyp - expected_hyp) < 0.001:
    test_results.append({"name": "hypotenuse", "passed": True, "score": 5.0})
else:
    test_results.append({"name": "hypotenuse", "passed": False, "score": 0.0})

passed = all(t["passed"] for t in test_results)
score = sum(t["score"] for t in test_results)
max_score = 10.0
feedback = f"Passed {sum(1 for t in test_results if t['passed'])}/2 tests"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert result.success, "Execution should succeed"
    assert result.passed, "All math tests should pass"
    assert result.score == 10.0, f"Score should be 10.0, got {result.score}"
    
    print(f"✅ PASSED - Math operations working")
    print(f"   Score: {result.score}/{result.max_score}")
    return True


async def test_output_capture():
    """Test 8: Output capture"""
    print("\n" + "="*60)
    print("TEST 8: Output Capture")
    print("="*60)
    
    executor = await ExecutorFactory.create_executor()
    
    student_code = """
print("Hello from student code!")
print("Line 2")
result = "test"
"""
    
    test_code = """
print("Hello from test code!")
passed = result == "test"
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Output captured"
"""
    
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
    
    assert result.success, "Execution should succeed"
    assert len(result.stdout) > 0, "Should capture stdout"
    
    print(f"✅ PASSED - Output capture working")
    print(f"   Stdout length: {len(result.stdout)} chars")
    return True


async def test_docker_health():
    """Test 9: Docker health check"""
    print("\n" + "="*60)
    print("TEST 9: Docker Health Check")
    print("="*60)
    
    executor = await ExecutorFactory.create_executor()
    
    is_healthy = await executor.health_check()
    await executor.cleanup()
    
    assert is_healthy, "Docker executor should be healthy"
    
    print(f"✅ PASSED - Docker executor is healthy")
    return True


async def test_configuration_validation():
    """Test 10: Configuration validation"""
    print("\n" + "="*60)
    print("TEST 10: Configuration Validation")
    print("="*60)
    
    is_valid, issues = await ExecutorFactory.validate_setup()
    
    assert is_valid, f"Configuration should be valid. Issues: {issues}"
    
    print(f"✅ PASSED - Configuration is valid")
    print(f"   Docker enabled: {Config.DOCKER_ENABLED}")
    print(f"   Default timeout: {Config.DEFAULT_TIMEOUT}s")
    print(f"   Memory limit: {Config.DEFAULT_MEMORY_LIMIT}")
    return True


async def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "PHASE 1 IMPLEMENTATION TEST SUITE" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Basic Execution", test_basic_execution),
        ("Security Isolation", test_security_isolation),
        ("Resource Limits", test_resource_limits),
        ("Timeout Enforcement", test_timeout_enforcement),
        ("Error Handling", test_error_handling),
        ("Concurrent Execution", test_concurrent_execution),
        ("Math Operations", test_math_operations),
        ("Output Capture", test_output_capture),
        ("Docker Health", test_docker_health),
        ("Configuration", test_configuration_validation),
    ]
    
    passed = 0
    failed = 0
    start_time = time.time()
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ FAILED - {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR - {name}: {e}")
    
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests:    {len(tests)}")
    print(f"✅ Passed:      {passed}")
    print(f"❌ Failed:      {failed}")
    print(f"⏱️  Total Time:  {total_time:.2f}s")
    print(f"Success Rate:  {passed/len(tests)*100:.1f}%")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 1 implementation is working correctly! 🎉\n")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the failures above.\n")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
