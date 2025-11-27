"""
End-to-End Test Data Setup
Creates teachers, students, assignments with questions, test cases, and sample submissions
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from datetime import datetime, timedelta

from models.assignment import Assignment, Question
from models.user import Teacher, Student
from models.test_case import SingleCellTestCase
from models.submission import Submission, CellAnswer, GradeStatus
from config import Settings

settings = Settings()

async def setup_e2e_test_data():
    """Setup complete end-to-end test environment"""
    
    # Initialize database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    await init_beanie(
        database=database,
        document_models=[Assignment, Teacher, Student, SingleCellTestCase, Submission]
    )
    
    print("=" * 60)
    print("🚀 SETTING UP END-TO-END TEST DATA")
    print("=" * 60)
    
    # ============================================
    # 1. CREATE TEACHERS
    # ============================================
    print("\n📚 Creating Teachers...")
    
    teachers = []
    teacher_data = [
        {"email": "john.smith@university.edu", "name": "Dr. John Smith"},
        {"email": "sarah.johnson@university.edu", "name": "Prof. Sarah Johnson"},
    ]
    
    for td in teacher_data:
        existing = await Teacher.find_one(Teacher.email == td["email"])
        if existing:
            teacher = existing
            print(f"   ✓ Using existing: {teacher.name}")
        else:
            teacher = Teacher(**td)
            await teacher.insert()
            print(f"   ✅ Created: {teacher.name}")
        teachers.append(teacher)
    
    # ============================================
    # 2. CREATE STUDENTS
    # ============================================
    print("\n👨‍🎓 Creating Students...")
    
    students = []
    student_data = [
        {"email": "alice.wonder@student.edu", "name": "Alice Wonder"},
        {"email": "bob.builder@student.edu", "name": "Bob Builder"},
        {"email": "charlie.brown@student.edu", "name": "Charlie Brown"},
    ]
    
    for sd in student_data:
        existing = await Student.find_one(Student.email == sd["email"])
        if existing:
            student = existing
            print(f"   ✓ Using existing: {student.name}")
        else:
            student = Student(**sd)
            await student.insert()
            print(f"   ✅ Created: {student.name}")
        students.append(student)
    
    # ============================================
    # 3. CREATE ASSIGNMENTS WITH QUESTIONS
    # ============================================
    print("\n📝 Creating Assignments...")
    
    assignments = []
    
    # Assignment 1: Basic Python (Easy)
    assignment1 = Assignment(
        title="Python Basics - Week 1",
        description="""
# Introduction to Python Programming

Welcome to your first Python assignment! This will test fundamental concepts.

**Learning Objectives:**
- Understand basic data types
- Write simple functions
- Use arithmetic operations

**Grading:**
- Each question has different point values
- Partial credit available
- Test your code before submitting!
        """.strip(),
        questions=[
            Question(
                question_number=1,
                title="Hello Function",
                description="""
## Task
Create a function `greet(name)` that returns a greeting message.

**Requirements:**
- Return a string in the format: "Hello, {name}!"
- Handle empty string (return "Hello, World!")

**Examples:**
```python
greet("Alice")    # Returns "Hello, Alice!"
greet("")         # Returns "Hello, World!"
```
                """.strip(),
                cell_id="cell_1",
                points=5.0,
                starter_code='def greet(name):\n    # TODO: Return greeting\n    pass\n'
            ),
            Question(
                question_number=2,
                title="Simple Math",
                description="""
## Task
Write a function `add_two_numbers(a, b)` that returns the sum.

**Examples:**
```python
add_two_numbers(5, 3)     # Returns 8
add_two_numbers(-1, 1)    # Returns 0
```
                """.strip(),
                cell_id="cell_2",
                points=5.0,
                starter_code='def add_two_numbers(a, b):\n    # TODO: Return sum\n    pass\n'
            ),
        ],
        teacher_id=str(teachers[0].id),
        due_date=datetime.now() + timedelta(days=3)
    )
    await assignment1.insert()
    assignments.append(assignment1)
    print(f"   ✅ {assignment1.title} (ID: {assignment1.id})")
    
    # Assignment 2: Intermediate Python
    assignment2 = Assignment(
        title="String & List Operations - Week 2",
        description="""
# String and List Manipulation

Master string and list operations in Python.
        """.strip(),
        questions=[
            Question(
                question_number=1,
                title="String Length",
                description="""
## Task
Write `get_length(text)` that returns the length of a string.

**Example:**
```python
get_length("hello")  # Returns 5
```
                """.strip(),
                cell_id="cell_1",
                points=10.0,
                starter_code='def get_length(text):\n    # TODO\n    pass\n'
            ),
            Question(
                question_number=2,
                title="List Sum",
                description="""
## Task
Write `sum_list(numbers)` that returns sum of all numbers.

**Example:**
```python
sum_list([1, 2, 3])  # Returns 6
```
                """.strip(),
                cell_id="cell_2",
                points=15.0,
                starter_code='def sum_list(numbers):\n    # TODO\n    pass\n'
            ),
        ],
        teacher_id=str(teachers[0].id),
        due_date=datetime.now() + timedelta(days=7)
    )
    await assignment2.insert()
    assignments.append(assignment2)
    print(f"   ✅ {assignment2.title} (ID: {assignment2.id})")
    
    # Assignment 3: Advanced (from previous script)
    assignment3 = await Assignment.find_one(Assignment.title == "Python Programming Fundamentals")
    if assignment3:
        assignments.append(assignment3)
        print(f"   ✓ Using existing: {assignment3.title}")
    
    # ============================================
    # 4. CREATE TEST CASES
    # ============================================
    print("\n🧪 Creating Test Cases...")
    
    test_cases = []
    
    # Test cases for Assignment 1
    test_cases.extend([
        SingleCellTestCase(
            assignment_id=str(assignment1.id),
            question_number=1,
            cell_id="cell_1",
            testcase_name="Test Greet Function",
            testcase_function="""
def test_greet(student_code):
    exec(student_code, globals())
    assert greet("Alice") == "Hello, Alice!", "Failed for 'Alice'"
    assert greet("") == "Hello, World!", "Failed for empty string"
    return True, "All tests passed!"
""",
            timeout=5,
            points=5.0,
            description="Test greeting function"
        ),
        SingleCellTestCase(
            assignment_id=str(assignment1.id),
            question_number=2,
            cell_id="cell_2",
            testcase_name="Test Add Function",
            testcase_function="""
def test_add(student_code):
    exec(student_code, globals())
    assert add_two_numbers(5, 3) == 8, "5 + 3 should be 8"
    assert add_two_numbers(-1, 1) == 0, "-1 + 1 should be 0"
    assert add_two_numbers(0, 0) == 0, "0 + 0 should be 0"
    return True, "Addition tests passed!"
""",
            timeout=5,
            points=5.0,
            description="Test addition function"
        ),
    ])
    
    # Test cases for Assignment 2
    test_cases.extend([
        SingleCellTestCase(
            assignment_id=str(assignment2.id),
            question_number=1,
            cell_id="cell_1",
            testcase_name="Test String Length",
            testcase_function="""
def test_length(student_code):
    exec(student_code, globals())
    assert get_length("hello") == 5, "Length of 'hello' should be 5"
    assert get_length("") == 0, "Length of empty string should be 0"
    assert get_length("Python") == 6, "Length of 'Python' should be 6"
    return True, "Length tests passed!"
""",
            timeout=5,
            points=10.0,
            description="Test string length"
        ),
        SingleCellTestCase(
            assignment_id=str(assignment2.id),
            question_number=2,
            cell_id="cell_2",
            testcase_name="Test List Sum",
            testcase_function="""
def test_sum(student_code):
    exec(student_code, globals())
    assert sum_list([1, 2, 3]) == 6, "Sum of [1,2,3] should be 6"
    assert sum_list([]) == 0, "Sum of empty list should be 0"
    assert sum_list([-1, 1]) == 0, "Sum of [-1, 1] should be 0"
    return True, "Sum tests passed!"
""",
            timeout=5,
            points=15.0,
            description="Test list sum"
        ),
    ])
    
    for tc in test_cases:
        await tc.insert()
        print(f"   ✅ Q{tc.question_number} - {tc.testcase_name}")
    
    # ============================================
    # 5. CREATE SAMPLE SUBMISSIONS
    # ============================================
    print("\n📤 Creating Sample Submissions...")
    
    submissions = []
    
    # Alice's submission for Assignment 1 (correct answers)
    submission1 = Submission(
        assignment_id=str(assignment1.id),
        student_id=str(students[0].id),
        answers=[
            CellAnswer(
                cell_id="cell_1",
                code='def greet(name):\n    if name == "":\n        return "Hello, World!"\n    return f"Hello, {name}!"\n',
                score=5.0,
                max_score=5.0,
                feedback="Perfect!"
            ),
            CellAnswer(
                cell_id="cell_2",
                code='def add_two_numbers(a, b):\n    return a + b\n',
                score=5.0,
                max_score=5.0,
                feedback="Correct!"
            ),
        ],
        status=GradeStatus.COMPLETED,
        total_score=10.0,
        max_score=10.0,
        graded_at=datetime.now()
    )
    await submission1.insert()
    submissions.append(submission1)
    print(f"   ✅ {students[0].name} → {assignment1.title} (Score: 10/10)")
    
    # Bob's submission for Assignment 1 (partial credit)
    submission2 = Submission(
        assignment_id=str(assignment1.id),
        student_id=str(students[1].id),
        answers=[
            CellAnswer(
                cell_id="cell_1",
                code='def greet(name):\n    return "Hello, " + name + "!"\n',  # Wrong for empty string
                score=3.0,
                max_score=5.0,
                feedback="Doesn't handle empty string correctly"
            ),
            CellAnswer(
                cell_id="cell_2",
                code='def add_two_numbers(a, b):\n    return a + b\n',
                score=5.0,
                max_score=5.0,
                feedback="Correct!"
            ),
        ],
        status=GradeStatus.COMPLETED,
        total_score=8.0,
        max_score=10.0,
        graded_at=datetime.now()
    )
    await submission2.insert()
    submissions.append(submission2)
    print(f"   ✅ {students[1].name} → {assignment1.title} (Score: 8/10)")
    
    # Charlie's pending submission for Assignment 2
    submission3 = Submission(
        assignment_id=str(assignment2.id),
        student_id=str(students[2].id),
        answers=[
            CellAnswer(
                cell_id="cell_1",
                code='def get_length(text):\n    return len(text)\n',
                score=0.0,
                max_score=10.0
            ),
            CellAnswer(
                cell_id="cell_2",
                code='def sum_list(numbers):\n    return sum(numbers)\n',
                score=0.0,
                max_score=15.0
            ),
        ],
        status=GradeStatus.PENDING,
        total_score=0.0,
        max_score=25.0
    )
    await submission3.insert()
    submissions.append(submission3)
    print(f"   ✅ {students[2].name} → {assignment2.title} (Pending)")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "=" * 60)
    print("✨ TEST DATA SETUP COMPLETE!")
    print("=" * 60)
    
    print(f"\n👥 Users Created:")
    print(f"   Teachers: {len(teachers)}")
    for t in teachers:
        print(f"      - {t.name} ({t.email})")
    print(f"   Students: {len(students)}")
    for s in students:
        print(f"      - {s.name} ({s.email})")
    
    print(f"\n📝 Assignments Created: {len(assignments)}")
    for a in assignments:
        q_count = len(a.questions) if a.questions else 0
        total_pts = sum(q.points for q in a.questions) if a.questions else 0
        print(f"   - {a.title}")
        print(f"     Questions: {q_count} | Points: {total_pts} | Due: {a.due_date.strftime('%Y-%m-%d')}")
    
    print(f"\n🧪 Test Cases Created: {len(test_cases)}")
    
    print(f"\n📤 Submissions Created: {len(submissions)}")
    for sub in submissions:
        assign = next((a for a in assignments if str(a.id) == sub.assignment_id), None)
        stud = next((s for s in students if str(s.id) == sub.student_id), None)
        if assign and stud:
            print(f"   - {stud.name} → {assign.title} ({sub.status.value})")
    
    print("\n" + "=" * 60)
    print("🎯 TEST SCENARIOS YOU CAN TRY:")
    print("=" * 60)
    
    print("\n1️⃣  STUDENT VIEW:")
    print("   - Login as any student")
    print("   - View available assignments")
    print("   - Open assignment in notebook view")
    print("   - Write code and test it")
    print("   - Submit assignment")
    
    print("\n2️⃣  TEACHER VIEW:")
    print("   - Login as a teacher")
    print("   - Create new assignment with questions")
    print("   - Add test cases for questions")
    print("   - View student submissions")
    print("   - Grade submissions")
    
    print("\n3️⃣  TESTING WORKFLOW:")
    print("   - Student writes code for Question 1")
    print("   - Clicks 'Run Tests' to see results")
    print("   - Fixes code based on feedback")
    print("   - Moves to next question")
    print("   - Submits all answers together")
    
    print("\n📊 DATABASE INFO:")
    print(f"   Database: {settings.database_name}")
    print(f"   URL: {settings.mongodb_url}")
    
    print("\n🔗 ASSIGNMENT URLS:")
    for a in assignments:
        print(f"   /assignment/{a.id}/notebook")
    
    print("\n" + "=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_e2e_test_data())
