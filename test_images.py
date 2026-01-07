# Quick Test Script for Docker Images
# Usage: python test_images.py

import asyncio
import sys
sys.path.append('backend')

from utils.executor_factory import ExecutorFactory
from utils.executor_interface import ExecutionConfig, ExecutionLanguage

async def test_base_image():
    """Test base image with standard library"""
    print("\n=== Testing Base Image ===")
    executor = await ExecutorFactory.get_default_executor()
    
    config = ExecutionConfig(
        language=ExecutionLanguage.PYTHON,
        docker_image="grader-python-base:latest"
    )
    
    student_code = """
import math
result = math.pi * 5 ** 2
"""
    
    test_code = """
expected = 78.53981633974483
passed = abs(result - expected) < 0.001
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Correct!" if passed else "Incorrect"
"""
    
    result = await executor.execute(student_code, test_code, config)
    print(f"Success: {result.success}")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score}/{result.max_score}")
    print(f"Feedback: {result.feedback}")

async def test_numpy_image():
    """Test numpy image"""
    print("\n=== Testing NumPy Image ===")
    executor = await ExecutorFactory.get_default_executor()
    
    config = ExecutionConfig(
        language=ExecutionLanguage.PYTHON,
        docker_image="grader-python-numpy:latest"
    )
    
    student_code = """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
result = np.mean(arr)
"""
    
    test_code = """
expected = 3.0
passed = abs(result - expected) < 0.001
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Correct!" if passed else f"Expected {expected}, got {result}"
"""
    
    result = await executor.execute(student_code, test_code, config)
    print(f"Success: {result.success}")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score}/{result.max_score}")
    print(f"Feedback: {result.feedback}")

async def test_datascience_image():
    """Test datascience image"""
    print("\n=== Testing Data Science Image ===")
    executor = await ExecutorFactory.get_default_executor()
    
    config = ExecutionConfig(
        language=ExecutionLanguage.PYTHON,
        docker_image="grader-python-datascience:latest"
    )
    
    student_code = """
import numpy as np
import pandas as pd
from scipy import stats

data = [1, 2, 3, 4, 5]
result = np.mean(data)
"""
    
    test_code = """
expected = 3.0
passed = abs(result - expected) < 0.001
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "All packages available!" if passed else "Error"
"""
    
    result = await executor.execute(student_code, test_code, config)
    print(f"Success: {result.success}")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.score}/{result.max_score}")
    print(f"Feedback: {result.feedback}")

async def main():
    print("Testing Docker Images...")
    print("=" * 50)
    
    try:
        await test_base_image()
        await test_numpy_image()
        await test_datascience_image()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
