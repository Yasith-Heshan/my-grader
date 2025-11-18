# Quick Start: MongoDB Grader for Teachers

## 🚀 Create Your First Assignment in 5 Minutes

### Step 1: Create Assignment
```python
from services.assignment_service import create_assignment
from schemas import AssignmentCreate

assignment = await create_assignment(AssignmentCreate(
    title="Python Basics",
    description="Test fundamental Python skills",
    teacher_id=your_teacher_id
))
```

### Step 2: Add Test Cases (Choose Your Style)

#### Style A: Custom Test Function (Most Flexible)
```python
from services.assignment_service import add_test_case_with_function

def test_my_function(submission):
    if 'my_function' not in submission:
        return {"score": 0, "feedback": "Function not found"}
    
    func = submission['my_function']
    result = func(5)
    
    if result == 25:
        return {"score": 1.0, "feedback": "✅ Perfect!"}
    else:
        return {"score": 0, "feedback": f"❌ Expected 25, got {result}"}

await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="test_square",
    test_function=test_my_function,
    points=10.0,
    description="Test squaring function"
)
```

#### Style B: Helper Functions (Quick & Easy)
```python
from services.test_utils import create_function_test

# Create test with multiple cases
test = create_function_test(
    'square',
    [
        {"input": 5, "expected": 25},
        {"input": 3, "expected": 9},
        {"input": 0, "expected": 0}
    ],
    partial_credit=True  # Give partial credit for some correct
)

await add_test_case_with_function(
    assignment_id=str(assignment.id),
    test_name="test_square",
    test_function=test,
    points=10.0
)
```

## 📚 Common Test Patterns

### Test a Math Function
```python
from services.test_utils import create_math_test

test = create_math_test(
    'circle_area',
    [
        {"input": 1, "expected": 3.14159},
        {"input": 2, "expected": 12.56637}
    ],
    tolerance=0.001  # Allow small floating-point errors
)
```

### Test a DataFrame
```python
from services.test_utils import create_dataframe_test

test = create_dataframe_test(
    'student_data',
    {
        "min_rows": 10,
        "columns": ['name', 'age', 'grade'],
        "no_nulls": True
    }
)
```

### Test an Algorithm
```python
from services.test_utils import create_algorithm_test

test = create_algorithm_test(
    'my_sort',
    [
        {"input": [3, 1, 4, 1, 5], "expected": [1, 1, 3, 4, 5]},
        {"input": [], "expected": []}
    ],
    check_efficiency=True  # Time the execution
)
```

## 🎯 Test Result Formats

Your test function can return:

### 1. Boolean (Pass/Fail)
```python
return True   # Full credit
return False  # No credit
```

### 2. Float (Partial Credit)
```python
return 0.75  # 75% credit (must be 0.0 to 1.0)
```

### 3. Dict (Detailed Feedback)
```python
return {
    "score": 0.8,
    "feedback": "✅ 4/5 tests passed\n❌ Failed edge case with empty list"
}
```

## ⚙️ Advanced Options

### Custom Timeout
```python
await add_test_case_with_function(
    test_function=my_test,
    timeout=60.0,  # 60 seconds
    points=10.0
)
```

### Multiple Test Cases in One Function
```python
def comprehensive_test(submission):
    score = 0
    max_score = 3
    feedback = []
    
    # Test 1: Function exists
    if 'my_func' in submission:
        score += 1
        feedback.append("✅ Function found")
    else:
        return {"score": 0, "feedback": "❌ Function not found"}
    
    # Test 2: Returns correct type
    result = submission['my_func'](5)
    if isinstance(result, int):
        score += 1
        feedback.append("✅ Returns integer")
    else:
        feedback.append("❌ Should return integer")
    
    # Test 3: Correct value
    if result == 25:
        score += 1
        feedback.append("✅ Correct value")
    else:
        feedback.append(f"❌ Expected 25, got {result}")
    
    return {
        "score": score / max_score,
        "feedback": "\n".join(feedback)
    }
```

## 📝 Complete Example

```python
import asyncio
from services.assignment_service import create_assignment, add_test_case_with_function
from services.test_utils import create_function_test, create_dataframe_test
from schemas import AssignmentCreate

async def create_homework():
    # Create assignment
    assignment = await create_assignment(AssignmentCreate(
        title="Homework 1",
        description="Functions and data",
        teacher_id="teacher_123"
    ))
    
    # Add function test
    func_test = create_function_test(
        'double',
        [{"input": 5, "expected": 10}]
    )
    await add_test_case_with_function(
        assignment_id=str(assignment.id),
        test_name="test_double",
        test_function=func_test,
        points=10.0
    )
    
    # Add DataFrame test
    df_test = create_dataframe_test(
        'my_data',
        {"min_rows": 5, "columns": ['A', 'B']}
    )
    await add_test_case_with_function(
        assignment_id=str(assignment.id),
        test_name="test_dataframe",
        test_function=df_test,
        points=15.0
    )
    
    print(f"✅ Created assignment: {assignment.id}")
    print(f"📊 Total points: 25")

# Run it
asyncio.run(create_homework())
```

## 🔍 View Results

```python
from services.grader_service import grade_submission, get_grading_result

# Grade a submission
result = await grade_submission(submission_id)

print(f"Score: {result.total_score}/{result.max_score}")
print(f"Percentage: {result.percentage:.1f}%")

for item in result.items:
    print(f"\n{item.test_case_id}:")
    print(f"  Score: {item.score}/{item.max_score}")
    print(f"  Feedback: {item.feedback}")
```

## 💡 Tips

1. **Start Simple**: Begin with helper functions
2. **Test Your Tests**: Run with sample submissions first
3. **Clear Feedback**: Students need to understand what went wrong
4. **Partial Credit**: Reward partially correct solutions
5. **Reasonable Timeouts**: Most tests should complete in < 5 seconds

## 📖 Full Documentation

- **MONGODB_GRADER_GUIDE.md** - Complete guide
- **example_usage.py** - Working example
- **test_utils.py** - Helper function reference

## ❓ Common Questions

**Q: Can I test multiple functions in one test case?**  
A: Yes! Your test function receives the entire submission dict.

**Q: What if a student's code crashes?**  
A: Exceptions are caught and returned as feedback with 0 score.

**Q: Can I give partial credit?**  
A: Yes! Return a float (0.0-1.0) or dict with score.

**Q: How do I test DataFrames?**  
A: Use `create_dataframe_test()` helper or check in custom function.

**Q: What about timeout?**  
A: Set `timeout` parameter (default 30s). Tests exceeding this fail automatically.

## 🎉 You're Ready!

Start creating assignments with powerful, flexible test cases. Students get immediate, detailed feedback. You get automatic grading with partial credit support. Win-win! 🚀
