"""
Test utility functions for creating common test types
These functions help teachers create test cases easily, similar to LocalGrader
"""
from typing import List, Dict, Callable, Any
import numpy as np
import pandas as pd


def create_function_test(
    function_name: str, 
    test_cases: List[Dict], 
    partial_credit: bool = True
) -> Callable:
    """
    Create a test that checks if a function produces expected outputs
    
    Args:
        function_name: Name of the function to test
        test_cases: List of {"input": input_args, "expected": expected_output}
        partial_credit: Whether to give partial credit for some correct answers
        
    Returns:
        Test function that can be used with add_test_case
        
    Example:
        test_func = create_function_test(
            'circle_area',
            [
                {"input": 1, "expected": 3.14159},
                {"input": 2, "expected": 12.56637},
            ]
        )
    """
    def test_function(submission_data):
        if function_name not in submission_data:
            return {
                "score": 0, 
                "feedback": f"❌ Function '{function_name}' not found in submission"
            }
        
        func = submission_data[function_name]
        
        if not callable(func):
            return {
                "score": 0, 
                "feedback": f"❌ '{function_name}' is not a callable function"
            }
        
        passed = 0
        total = len(test_cases)
        feedback_parts = []
        
        for i, test_case in enumerate(test_cases):
            try:
                if isinstance(test_case["input"], (list, tuple)):
                    result = func(*test_case["input"])
                else:
                    result = func(test_case["input"])
                
                # Check if results match (handles floats with tolerance)
                if isinstance(result, (int, float, np.ndarray)):
                    matches = np.allclose(result, test_case["expected"], rtol=1e-5)
                else:
                    matches = result == test_case["expected"]
                
                if matches:
                    passed += 1
                    feedback_parts.append(f"✅ Test {i+1}: Passed")
                else:
                    feedback_parts.append(
                        f"❌ Test {i+1}: Expected {test_case['expected']}, got {result}"
                    )
            
            except Exception as e:
                feedback_parts.append(f"❌ Test {i+1}: Error - {str(e)}")
        
        score = passed / total if partial_credit else (1 if passed == total else 0)
        feedback = f"Passed {passed}/{total} test cases\n" + "\n".join(feedback_parts)
        
        return {"score": score, "feedback": feedback}
    
    return test_function


def create_dataframe_test(
    variable_name: str, 
    expected_properties: Dict
) -> Callable:
    """
    Create a test for pandas DataFrame properties
    
    Args:
        variable_name: Name of the DataFrame variable
        expected_properties: Dict with expected properties:
            - "shape": Expected shape tuple
            - "columns": Expected column list
            - "dtypes": Expected data types dict
            - "min_rows": Minimum number of rows
            - "min_cols": Minimum number of columns
            - "no_nulls": Whether nulls are allowed
        
    Returns:
        Test function that can be used with add_test_case
        
    Example:
        test_func = create_dataframe_test(
            'student_data',
            {
                "min_rows": 10,
                "min_cols": 3,
                "columns": ['name', 'age', 'grade'],
                "no_nulls": True
            }
        )
    """
    def test_function(submission_data):
        if variable_name not in submission_data:
            return {
                "score": 0, 
                "feedback": f"❌ DataFrame '{variable_name}' not found"
            }
        
        df = submission_data[variable_name]
        
        if not isinstance(df, pd.DataFrame):
            return {
                "score": 0, 
                "feedback": f"❌ '{variable_name}' is not a pandas DataFrame"
            }
        
        score = 0
        max_score = len(expected_properties)
        feedback_parts = []
        
        for prop, expected in expected_properties.items():
            if prop == "shape":
                if df.shape == expected:
                    score += 1
                    feedback_parts.append(f"✅ Shape correct: {df.shape}")
                else:
                    feedback_parts.append(
                        f"❌ Shape incorrect: expected {expected}, got {df.shape}"
                    )
            
            elif prop == "min_rows":
                if df.shape[0] >= expected:
                    score += 1
                    feedback_parts.append(f"✅ Has at least {expected} rows: {df.shape[0]}")
                else:
                    feedback_parts.append(
                        f"❌ Need at least {expected} rows, got {df.shape[0]}"
                    )
            
            elif prop == "min_cols":
                if df.shape[1] >= expected:
                    score += 1
                    feedback_parts.append(f"✅ Has at least {expected} columns: {df.shape[1]}")
                else:
                    feedback_parts.append(
                        f"❌ Need at least {expected} columns, got {df.shape[1]}"
                    )
            
            elif prop == "columns":
                if list(df.columns) == expected:
                    score += 1
                    feedback_parts.append("✅ Columns correct")
                else:
                    missing = set(expected) - set(df.columns)
                    extra = set(df.columns) - set(expected)
                    msg = f"❌ Columns incorrect"
                    if missing:
                        msg += f" (missing: {missing})"
                    if extra:
                        msg += f" (extra: {extra})"
                    feedback_parts.append(msg)
            
            elif prop == "dtypes":
                correct_dtypes = all(
                    str(df[col].dtype) == expected[col] 
                    for col in expected if col in df.columns
                )
                if correct_dtypes:
                    score += 1
                    feedback_parts.append("✅ Data types correct")
                else:
                    feedback_parts.append("❌ Data types incorrect")
            
            elif prop == "no_nulls":
                null_count = df.isnull().sum().sum()
                if (expected and null_count == 0) or (not expected and null_count > 0):
                    score += 1
                    feedback_parts.append("✅ No missing values" if expected else "✅ Has missing values")
                else:
                    if expected:
                        feedback_parts.append(f"❌ Has {null_count} missing values")
                    else:
                        feedback_parts.append("❌ Should have missing values")
        
        final_score = score / max_score
        feedback = (
            f"DataFrame check: {score}/{max_score} properties correct\n" + 
            "\n".join(feedback_parts)
        )
        
        return {"score": final_score, "feedback": feedback}
    
    return test_function


def create_algorithm_test(
    function_name: str,
    test_cases: List[Dict],
    check_efficiency: bool = False
) -> Callable:
    """
    Create a test for algorithm implementations (e.g., sorting, searching)
    
    Args:
        function_name: Name of the function to test
        test_cases: List of {"input": input_data, "expected": expected_output}
        check_efficiency: Whether to measure execution time
        
    Returns:
        Test function that can be used with add_test_case
        
    Example:
        test_func = create_algorithm_test(
            'my_sort',
            [
                {"input": [3, 1, 4, 1, 5], "expected": [1, 1, 3, 4, 5]},
                {"input": [], "expected": []},
            ]
        )
    """
    def test_function(submission_data):
        if function_name not in submission_data:
            return {
                "score": 0,
                "feedback": f"❌ Function '{function_name}' not found"
            }
        
        func = submission_data[function_name]
        
        if not callable(func):
            return {
                "score": 0,
                "feedback": f"❌ '{function_name}' is not a callable function"
            }
        
        passed = 0
        total = len(test_cases)
        feedback_parts = []
        execution_times = []
        
        for i, test_case in enumerate(test_cases):
            try:
                # Make a copy to avoid modifying original
                if isinstance(test_case["input"], list):
                    test_input = test_case["input"].copy()
                else:
                    test_input = test_case["input"]
                
                # Measure execution time if requested
                import time
                start = time.time()
                result = func(test_input)
                exec_time = time.time() - start
                execution_times.append(exec_time)
                
                if result == test_case["expected"]:
                    passed += 1
                    time_info = f" ({exec_time*1000:.2f}ms)" if check_efficiency else ""
                    feedback_parts.append(f"✅ Test {i+1}: Passed{time_info}")
                else:
                    feedback_parts.append(
                        f"❌ Test {i+1}: Expected {test_case['expected']}, got {result}"
                    )
            
            except Exception as e:
                feedback_parts.append(f"❌ Test {i+1}: Error - {str(e)}")
        
        score = passed / total
        feedback = f"Algorithm test: {passed}/{total} test cases passed\n"
        
        if check_efficiency and execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            feedback += f"Average execution time: {avg_time*1000:.2f}ms\n"
        
        feedback += "\n".join(feedback_parts)
        
        return {"score": score, "feedback": feedback}
    
    return test_function


def create_math_test(
    function_name: str,
    test_cases: List[Dict],
    tolerance: float = 1e-5
) -> Callable:
    """
    Create a test for mathematical functions with floating-point tolerance
    
    Args:
        function_name: Name of the function to test
        test_cases: List of {"input": input_args, "expected": expected_output}
        tolerance: Acceptable floating-point error
        
    Returns:
        Test function that can be used with add_test_case
        
    Example:
        test_func = create_math_test(
            'circle_area',
            [
                {"input": 1, "expected": 3.14159265},
                {"input": 2, "expected": 12.5663706},
            ],
            tolerance=0.001
        )
    """
    def test_function(submission_data):
        if function_name not in submission_data:
            return {
                "score": 0,
                "feedback": f"❌ Function '{function_name}' not found"
            }
        
        func = submission_data[function_name]
        
        if not callable(func):
            return {
                "score": 0,
                "feedback": f"❌ '{function_name}' is not a callable function"
            }
        
        passed = 0
        total = len(test_cases)
        feedback_parts = []
        
        for i, test_case in enumerate(test_cases):
            try:
                if isinstance(test_case["input"], (list, tuple)):
                    result = func(*test_case["input"])
                else:
                    result = func(test_case["input"])
                
                expected = test_case["expected"]
                
                # Check with tolerance
                if abs(result - expected) <= tolerance:
                    passed += 1
                    feedback_parts.append(
                        f"✅ Test {i+1}: Passed (result={result:.6f})"
                    )
                else:
                    diff = abs(result - expected)
                    feedback_parts.append(
                        f"❌ Test {i+1}: Expected {expected:.6f}, got {result:.6f} "
                        f"(difference: {diff:.6f}, tolerance: {tolerance})"
                    )
            
            except Exception as e:
                feedback_parts.append(f"❌ Test {i+1}: Error - {str(e)}")
        
        score = passed / total
        feedback = f"Math test: {passed}/{total} test cases passed\n" + "\n".join(feedback_parts)
        
        return {"score": score, "feedback": feedback}
    
    return test_function
