# MongoDB-Based Grader System

This document explains how to use the enhanced grader system that stores data in MongoDB instead of JSON files.

## Overview

The grader system has been migrated from the `LocalGrader` (which used JSON files) to a MongoDB-based system with the same powerful features:

- **Dynamic test functions** with partial credit support
- **Timeout protection** for test execution
- **Detailed feedback** generation
- **Multiple test result formats** (boolean, float, dict)
- **Utility functions** for creating common test types

## Key Changes

### 1. Test Case Model Enhancement

The `TestCase` model now supports:
- `serialized_function`: Base64-encoded pickled test function
- `timeout`: Maximum execution time (default: 30 seconds)
- `test_name`: Unique identifier for the test
- Both legacy `test_code` (simple) and `serialized_function` (advanced) modes

### 2. Enhanced Grader Service

The `grader_service.py` now handles:
- Deserializing and executing test functions
- Partial credit calculation (0.0 to 1.0 score)
- Timeout enforcement
- Multiple feedback formats

### 3. Helper Functions

New `test_utils.py` module provides:
- `create_function_test()` - Test function implementations
- `create_dataframe_test()` - Test pandas DataFrames
- `create_algorithm_test()` - Test algorithms with efficiency checks
- `create_math_test()` - Test math functions with tolerance

## Usage Examples

### Example 1: Create an Assignment with Dynamic Test Functions

```python
from services.assignment_service import create_assignment, add_test_case_with_function
from services.test_utils import create_function_test, create_dataframe_test
from schemas import AssignmentCreate
import math

# 1. Create an assignment
assignment_data = AssignmentCreate(
    title="Python Homework 1",
    description="Functions and DataFrames",
    teacher_id="teacher_123"
)
assignment = await create_assignment(assignment_data)

# 2. Create a test for circle area function
def test_circle_area(submission):
    """Test if student correctly implemented circle_area function"""
    if 'circle_area' not in submission:
        return {"score": 0, "feedback": "❌ Function 'circle_area' not found!"}
    
    func = submission['circle_area']
    test_cases = [
        (1, math.pi),
        (3, 9 * math.pi),
        (0, 0),
    ]
    
    score = 0
    feedback_parts = []
    
    for radius, expected in test_cases:
        try:
            result = func(radius)
            if abs(result - expected) < 0.001:
                score += 1
                feedback_parts.append(f"✅ Correct for radius={radius}")
            else:
                feedback_parts.append(f"❌ Wrong for radius={radius}")
        except Exception as e:
            feedback_parts.append(f"❌ Error: {str(e)}")
    
    final_score = score / len(test_cases)
    feedback = f"Score: {score}/{len(test_cases)}\n" + "\n".join(feedback_parts)
    
    return {"score": final_score, "feedback": feedback}

# Add the test to the assignment
await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="circle_area_test",
    test_function=test_circle_area,
    points=10.0,
    description="Test circle area calculation",
    timeout=30.0
)

# 3. Or use helper functions for common test types
test_func = create_function_test(
    'my_sort',
    [
        {"input": [3, 1, 4, 1, 5], "expected": [1, 1, 3, 4, 5]},
        {"input": [], "expected": []},
        {"input": [1], "expected": [1]},
    ],
    partial_credit=True
)

await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="sorting_test",
    test_function=test_func,
    points=20.0,
    description="Test sorting algorithm"
)
```

### Example 2: Using Test Utility Functions

```python
from services.test_utils import (
    create_function_test,
    create_dataframe_test,
    create_math_test,
    create_algorithm_test
)

# Test a math function with tolerance
math_test = create_math_test(
    'calculate_pi',
    [
        {"input": 100, "expected": 3.14159},
        {"input": 1000, "expected": 3.14159},
    ],
    tolerance=0.01
)

# Test a DataFrame
df_test = create_dataframe_test(
    'student_data',
    {
        "min_rows": 10,
        "min_cols": 3,
        "columns": ['name', 'age', 'grade'],
        "no_nulls": True
    }
)

# Test an algorithm with efficiency checking
algo_test = create_algorithm_test(
    'binary_search',
    [
        {"input": ([1, 2, 3, 4, 5], 3), "expected": 2},
        {"input": ([1, 2, 3, 4, 5], 6), "expected": -1},
    ],
    check_efficiency=True
)

# Add all tests to assignment
await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="math_test",
    test_function=math_test,
    points=15.0
)

await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="dataframe_test",
    test_function=df_test,
    points=15.0
)

await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="algorithm_test",
    test_function=algo_test,
    points=20.0
)
```

### Example 3: Student Submission and Grading

```python
from services.grader_service import grade_submission
from services.submission_service import create_submission, submit_item

# Student submits code
submission = await create_submission(
    assignment_id=str(assignment.id),
    student_id="student_456"
)

# Get test cases
test_cases = await get_test_cases(str(assignment.id))

# Submit code for each test
for test_case in test_cases:
    # Student's code
    student_code = """
import math

def circle_area(radius):
    return math.pi * radius * radius

def my_sort(arr):
    return sorted(arr)
"""
    
    await submit_item(
        submission_id=str(submission.id),
        test_case_id=str(test_case.id),
        submitted_code=student_code
    )

# Grade the submission
result = await grade_submission(str(submission.id))

print(f"Total Score: {result.total_score}/{result.max_score}")
print(f"Percentage: {result.percentage:.1f}%")
print(f"Status: {result.status}")

for item in result.items:
    print(f"\nTest: {item.test_case_id}")
    print(f"Score: {item.score}/{item.max_score}")
    print(f"Feedback: {item.feedback}")
```

## Test Result Formats

Your test function can return different formats:

### 1. Boolean (Pass/Fail)
```python
def test_function(submission):
    return True  # Full credit
    # or
    return False  # No credit
```

### 2. Float (Partial Credit)
```python
def test_function(submission):
    return 0.75  # 75% credit (must be between 0.0 and 1.0)
```

### 3. Dictionary (Detailed Feedback)
```python
def test_function(submission):
    return {
        "score": 0.8,  # 80% credit
        "feedback": "✅ 4/5 test cases passed\n❌ Failed edge case"
    }
```

## Migration Notes

### From LocalGrader to MongoDB

**Before (LocalGrader with JSON):**
```python
from local_grader import LocalGrader

grader = LocalGrader("homework_1")
grader.add_test_case(
    test_name="test1",
    test_function=my_test,
    points=10
)
result = grader.submit("student_123", submission_data)
```

**After (MongoDB-based):**
```python
from services.assignment_service import create_assignment, add_test_case_with_function

# Create assignment first
assignment = await create_assignment(AssignmentCreate(...))

# Add test cases
await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="test1",
    test_function=my_test,
    points=10.0
)

# Students submit through API
# Grading happens via grade_submission()
```

## Benefits of MongoDB Storage

1. **Scalability**: Handle thousands of submissions efficiently
2. **Concurrent Access**: Multiple teachers and students can access simultaneously
3. **Data Integrity**: ACID transactions ensure consistent data
4. **Query Performance**: Fast retrieval with indexes
5. **Backup & Recovery**: Built-in MongoDB backup tools
6. **Cloud Ready**: Easy deployment with MongoDB Atlas

## API Integration

The grader integrates with the FastAPI backend:

- `POST /api/teacher/assignments` - Create assignment
- `POST /api/teacher/assignments/{id}/tests` - Add test cases
- `POST /api/student/submissions` - Submit code
- `POST /api/student/submissions/{id}/grade` - Grade submission
- `GET /api/student/submissions/{id}/results` - Get results

## Testing the System

See `test_api.py` for comprehensive API tests that verify:
- Assignment creation
- Test case addition
- Submission grading
- Result retrieval

Run tests:
```bash
pytest backend/test_api.py -v
```

## Performance Considerations

- Test functions are executed synchronously (avoid long-running operations)
- Timeout defaults to 30 seconds (configurable per test)
- Large DataFrames are summarized in submission records
- Function objects are pickled and base64-encoded for storage

## Security Notes

- Test functions can execute arbitrary Python code
- Ensure test functions are from trusted sources only
- Consider sandboxing for production environments
- Validate student code before execution
