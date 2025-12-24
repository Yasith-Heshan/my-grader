"""
Example usage of the Docker executor system

This file demonstrates how to use the new secure Docker-based code execution system.
"""
import asyncio
from utils.executor_interface import ExecutionConfig, ExecutionLanguage
from utils.executor_factory import ExecutorFactory
from config.executor_config import ExecutorConfig as Config


async def example_basic_execution():
    """Example: Basic code execution"""
    print("=" * 60)
    print("Example 1: Basic Code Execution")
    print("=" * 60)
    
    # Create executor (automatically selects Docker or local based on config)
    executor = await ExecutorFactory.create_executor()
    
    # Student code
    student_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

result_add = add(5, 3)
result_mul = multiply(4, 7)
"""
    
    # Test code
    test_code = """
# Test the functions
test_results = []

# Test 1: Addition
if result_add == 8:
    test_results.append({"name": "test_add", "passed": True, "score": 5.0})
else:
    test_results.append({"name": "test_add", "passed": False, "score": 0.0})

# Test 2: Multiplication
if result_mul == 28:
    test_results.append({"name": "test_mul", "passed": True, "score": 5.0})
else:
    test_results.append({"name": "test_mul", "passed": False, "score": 0.0})

# Set results
passed = all(t["passed"] for t in test_results)
score = sum(t["score"] for t in test_results)
max_score = 10.0
feedback = f"Passed {sum(1 for t in test_results if t['passed'])}/2 tests"
"""
    
    # Execute
    result = await executor.execute(student_code, test_code)
    
    # Display results
    print(f"\nSuccess: {result.success}")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score}/{result.max_score}")
    print(f"Feedback: {result.feedback}")
    print(f"Execution Time: {result.execution_time:.3f}s")
    
    # Cleanup
    await executor.cleanup()


async def example_with_custom_config():
    """Example: Execution with custom configuration"""
    print("\n" + "=" * 60)
    print("Example 2: Custom Configuration")
    print("=" * 60)
    
    # Create custom configuration
    config = ExecutionConfig(
        language=ExecutionLanguage.PYTHON,
        timeout=5,
        memory_limit="128m",
        cpu_quota=25000,  # 25% of one core
        network_disabled=True,
        read_only_rootfs=True
    )
    
    # Create executor with custom config
    executor = await ExecutorFactory.create_executor(config)
    
    student_code = """
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

area = calculate_circle_area(5)
"""
    
    test_code = """
# Test circle area calculation
expected = 78.53981633974483
tolerance = 0.0001

if abs(area - expected) < tolerance:
    passed = True
    score = 10.0
    feedback = "Correct! Circle area calculated accurately."
else:
    passed = False
    score = 0.0
    feedback = f"Incorrect. Expected ~{expected}, got {area}"

max_score = 10.0
"""
    
    result = await executor.execute(student_code, test_code)
    
    print(f"\nSuccess: {result.success}")
    print(f"Score: {result.score}/{result.max_score}")
    print(f"Feedback: {result.feedback}")
    print(f"Memory Limit: {config.memory_limit}")
    print(f"CPU Quota: {config.cpu_quota}")
    
    await executor.cleanup()


async def example_timeout_handling():
    """Example: Handling timeout scenarios"""
    print("\n" + "=" * 60)
    print("Example 3: Timeout Handling")
    print("=" * 60)
    
    config = ExecutionConfig(timeout=2)  # 2 second timeout
    executor = await ExecutorFactory.create_executor(config)
    
    # Code that takes too long (infinite loop)
    student_code = """
import time

def slow_function():
    # This will timeout
    time.sleep(10)
    return "done"

result = slow_function()
"""
    
    test_code = """
passed = result == "done"
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Test completed"
"""
    
    result = await executor.execute(student_code, test_code)
    
    print(f"\nSuccess: {result.success}")
    print(f"Timeout Occurred: {result.timeout_occurred}")
    print(f"Error: {result.error_message}")
    print(f"Feedback: {result.feedback}")
    
    await executor.cleanup()


async def example_error_handling():
    """Example: Handling code errors"""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    executor = await ExecutorFactory.create_executor()
    
    # Code with errors
    student_code = """
def divide(a, b):
    return a / b

# This will cause division by zero
result = divide(10, 0)
"""
    
    test_code = """
passed = result == 5
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Test completed"
"""
    
    result = await executor.execute(student_code, test_code)
    
    print(f"\nSuccess: {result.success}")
    print(f"Error: {result.error_message}")
    print(f"Stderr: {result.stderr[:200] if result.stderr else 'None'}")
    
    await executor.cleanup()


async def example_system_validation():
    """Example: Validate system setup"""
    print("\n" + "=" * 60)
    print("Example 5: System Validation")
    print("=" * 60)
    
    # Check configuration
    print("\nConfiguration:")
    print(f"Docker Enabled: {Config.DOCKER_ENABLED}")
    print(f"Fallback to Local: {Config.FALLBACK_TO_LOCAL}")
    print(f"Default Timeout: {Config.DEFAULT_TIMEOUT}s")
    print(f"Memory Limit: {Config.DEFAULT_MEMORY_LIMIT}")
    print(f"Max Concurrent: {Config.MAX_CONCURRENT_CONTAINERS}")
    
    # Validate setup
    print("\nValidating setup...")
    is_valid, issues = await ExecutorFactory.validate_setup()
    
    if is_valid:
        print("✓ System is properly configured!")
    else:
        print("✗ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Test executor
    print("\nTesting executor...")
    executor = await ExecutorFactory.get_default_executor()
    
    if await executor.health_check():
        print("✓ Executor is healthy!")
    else:
        print("✗ Executor health check failed!")
    
    await executor.cleanup()


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Docker Executor Usage Examples" + " " * 17 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        await example_basic_execution()
        await example_with_custom_config()
        await example_timeout_handling()
        await example_error_handling()
        await example_system_validation()
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
