# Manual Testing Guide - Phase 3

## Quick Manual Test Cases

### Test Case 1: Perfect Score (Should get 100%)

**Student Code:**
```python
x = 10
result = 6 * 7
name = 'Test Student'
sum_value = 5 + 10
```

**Expected Result:** Score close to 100% (all tests should pass)

---

### Test Case 2: Partial Credit (Should get ~50%)

**Student Code:**
```python
x = 20
result = 6 * 7
name = 'Test'
sum_value = 10
```

**Expected Result:** Score around 50% (2 correct, 2 wrong)

---

### Test Case 3: Syntax Error

**Student Code:**
```python
x = 10
result = 6 * 7
name = 'Test
sum_value = 5 + 10
```

**Expected Result:** Error message, 0 score

---

### Test Case 4: Runtime Error

**Student Code:**
```python
x = 1 / 0
result = 6 * 7
name = 'Test'
sum_value = 5 + 10
```

**Expected Result:** Error message with "ZeroDivisionError", 0 score

---

### Test Case 5: Simple Math (Should pass)

**Student Code:**
```python
x = 10
```

**Expected for cell_1:** Should pass (x = 10 is correct)

---

### Test Case 6: Wrong Value (Should fail)

**Student Code:**
```python
x = 5
```

**Expected for cell_1:** Should fail (expected x = 10, got 5)

---

## How to Test Manually

### Option 1: Using Python REPL

```python
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Submission, Student, Assignment, GradeStatus
from services.grader_service import grade_submission
from datetime import datetime

async def manual_test():
    # Connect to database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.grading_system_test
    await init_beanie(
        database=db,
        document_models=[Submission, Student, Assignment]
    )
    
    # Get or create student
    student = await Student.find_one(Student.email == "test@example.com")
    if not student:
        student = Student(
            name="Manual Test Student",
            email="test@example.com",
            student_id="MANUAL001",
            password_hash="test"
        )
        await student.save()
    
    # Get assignment
    assignment = await Assignment.find_one(Assignment.title == "Python Basics - Variables and Math")
    if not assignment:
        print("❌ Assignment not found. Run test_phase3_manual.py first to create it.")
        return
    
    # TEST CASE 1: Perfect Score
    print("\n" + "="*60)
    print("TEST 1: PERFECT SCORE")
    print("="*60)
    
    code = """x = 10
result = 6 * 7
name = 'Test Student'
sum_value = 5 + 10
"""
    
    submission = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=code,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    await submission.save()
    
    print(f"Submission ID: {submission.id}")
    print(f"Grading...")
    
    result = await grade_submission(str(submission.id))
    
    print(f"\nResults:")
    print(f"  Status: {result.status}")
    print(f"  Score: {result.total_score}/{result.max_score}")
    print(f"  Percentage: {result.percentage:.1f}%")
    print(f"  Message: {result.message}")
    
    # TEST CASE 2: Partial Credit
    print("\n" + "="*60)
    print("TEST 2: PARTIAL CREDIT")
    print("="*60)
    
    code2 = """x = 20
result = 6 * 7
name = 'Test'
sum_value = 10
"""
    
    submission2 = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=code2,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    await submission2.save()
    
    print(f"Submission ID: {submission2.id}")
    print(f"Grading...")
    
    result2 = await grade_submission(str(submission2.id))
    
    print(f"\nResults:")
    print(f"  Score: {result2.total_score}/{result2.max_score}")
    print(f"  Percentage: {result2.percentage:.1f}%")
    
    # TEST CASE 3: Error Handling
    print("\n" + "="*60)
    print("TEST 3: ERROR HANDLING")
    print("="*60)
    
    code3 = """x = 1 / 0
result = 6 * 7
"""
    
    submission3 = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=code3,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    await submission3.save()
    
    print(f"Submission ID: {submission3.id}")
    print(f"Grading...")
    
    result3 = await grade_submission(str(submission3.id))
    
    print(f"\nResults:")
    print(f"  Score: {result3.total_score}/{result3.max_score}")
    print(f"  Percentage: {result3.percentage:.1f}%")
    print(f"  Message: {result3.message}")

asyncio.run(manual_test())
```

**To run:**
```powershell
cd backend
python
# Then paste the code above
```

---

### Option 2: Using evaluate_single_cell (Test individual questions)

```python
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Assignment
from services.grader_service import evaluate_single_cell

async def test_single_cell():
    # Connect to database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.grading_system_test
    await init_beanie(database=db, document_models=[Assignment])
    
    # Get assignment
    assignment = await Assignment.find_one(Assignment.title == "Python Basics - Variables and Math")
    if not assignment:
        print("❌ Assignment not found")
        return
    
    # TEST: cell_1 - Correct answer
    print("\n" + "="*60)
    print("TEST: Cell 1 - Correct (x = 10)")
    print("="*60)
    
    result1 = await evaluate_single_cell(
        assignment_id=str(assignment.id),
        cell_id="cell_1",
        student_code="x = 10",
        timeout=5
    )
    
    print(f"Score: {result1['score']}/{result1['max_score']}")
    print(f"Success: {result1['success']}")
    print(f"Feedback: {result1.get('feedback', 'N/A')}")
    
    # TEST: cell_1 - Wrong answer
    print("\n" + "="*60)
    print("TEST: Cell 1 - Wrong (x = 5)")
    print("="*60)
    
    result2 = await evaluate_single_cell(
        assignment_id=str(assignment.id),
        cell_id="cell_1",
        student_code="x = 5",
        timeout=5
    )
    
    print(f"Score: {result2['score']}/{result2['max_score']}")
    print(f"Success: {result2['success']}")
    
    # TEST: cell_2 - Correct calculation
    print("\n" + "="*60)
    print("TEST: Cell 2 - Correct (result = 42)")
    print("="*60)
    
    result3 = await evaluate_single_cell(
        assignment_id=str(assignment.id),
        cell_id="cell_2",
        student_code="result = 6 * 7",
        timeout=5
    )
    
    print(f"Score: {result3['score']}/{result3['max_score']}")
    print(f"Success: {result3['success']}")

asyncio.run(test_single_cell())
```

---

### Option 3: Simple Script File

Save this as `manual_test_simple.py`:

```python
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import Submission, Student, Assignment, GradeStatus
from services.grader_service import grade_submission
from datetime import datetime

async def test(code, description):
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(
        database=client.grading_system_test,
        document_models=[Submission, Student, Assignment]
    )
    
    student = await Student.find_one()
    assignment = await Assignment.find_one()
    
    if not student or not assignment:
        print("❌ No student or assignment found")
        return
    
    submission = Submission(
        student_id=str(student.id),
        assignment_id=str(assignment.id),
        code=code,
        status=GradeStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    await submission.save()
    
    result = await grade_submission(str(submission.id))
    
    print(f"✅ Score: {result.total_score}/{result.max_score} ({result.percentage:.1f}%)")
    print(f"   {result.message}")
    return result

# Run tests
async def main():
    # Test 1: Perfect
    await test("""x = 10
result = 6 * 7
name = 'Test'
sum_value = 5 + 10""", "Perfect Score")
    
    # Test 2: Partial
    await test("""x = 20
result = 6 * 7
name = 'Test'
sum_value = 10""", "Partial Credit")
    
    # Test 3: Error
    await test("""x = 1 / 0
result = 6 * 7""", "Runtime Error")

asyncio.run(main())
```

**Run with:**
```powershell
cd backend
python manual_test_simple.py
```

---

## What to Check

✅ **Scores are calculated correctly**
✅ **Docker containers are created and removed**
✅ **Execution completes within timeout**
✅ **Error messages are clear**
✅ **No security issues (exec() not used)**
✅ **Performance is acceptable (< 5s per submission)**

---

## Quick Verification Commands

```powershell
# Check Docker containers (should see grader-python-sandbox being used)
docker ps

# Check recent containers
docker ps -a | Select-Object -First 5

# Check database submissions
python -c "import asyncio; from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); db = client.grading_system_test; print(f'Submissions: {db.submissions.count_documents({})}'); print(f'Test cases: {db.single_cell_test_cases.count_documents({})}')"
```
