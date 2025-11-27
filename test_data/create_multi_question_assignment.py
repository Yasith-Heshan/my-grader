"""
Create a sample multi-question assignment with test cases
Run this script to populate the database with a complete assignment
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from datetime import datetime, timedelta

from models.assignment import Assignment, Question
from models.user import Teacher, Student
from models.test_case import SingleCellTestCase
from config import Settings

settings = Settings()

async def create_sample_assignment():
    """Create a multi-question Python assignment with test cases"""
    
    # Initialize database connection
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    
    await init_beanie(
        database=database,
        document_models=[Assignment, Teacher, Student, SingleCellTestCase]
    )
    
    print("🔗 Connected to MongoDB")
    
    # Get or create a teacher
    teacher = await Teacher.find_one(Teacher.email == "teacher@example.com")
    if not teacher:
        teacher = Teacher(
            email="teacher@example.com",
            name="Demo Teacher"
        )
        await teacher.insert()
        print("✅ Created demo teacher")
    
    teacher_id = str(teacher.id)
    
    # Create assignment with multiple questions
    assignment = Assignment(
        title="Python Programming Fundamentals",
        description="""
# Python Fundamentals Assignment

This assignment tests your understanding of basic Python programming concepts.

**Topics Covered:**
- Functions and return values
- String manipulation
- List operations
- Mathematical calculations

**Instructions:**
- Read each question carefully
- Write clean, well-commented code
- Test your code before submitting
- Each question is worth different points

Good luck! 🚀
        """.strip(),
        questions=[
            Question(
                question_number=1,
                title="Calculate Circle Area",
                description="""
## Task
Write a function `circle_area(radius)` that calculates and returns the area of a circle.

**Formula:** Area = π × r²

**Requirements:**
- Use `3.14159` as the value of π
- Return the result as a float
- Handle radius = 0 (should return 0)

**Examples:**
```python
circle_area(5)     # Returns 78.53975
circle_area(10)    # Returns 314.159
circle_area(0)     # Returns 0
```

**Hints:**
- Remember to use the `**` operator for exponentiation
- Make sure to return a numeric value
                """.strip(),
                cell_id="cell_1",
                points=10.0,
                starter_code="""def circle_area(radius):
    # TODO: Calculate the area of a circle
    # Formula: π × r²
    pass
"""
            ),
            Question(
                question_number=2,
                title="Reverse a String",
                description="""
## Task
Write a function `reverse_string(text)` that returns the reversed version of the input string.

**Requirements:**
- Return the string in reverse order
- Preserve all characters (including spaces and punctuation)
- Handle empty strings (return empty string)

**Examples:**
```python
reverse_string("hello")        # Returns "olleh"
reverse_string("Python!")      # Returns "!nohtyP"
reverse_string("A B C")        # Returns "C B A"
reverse_string("")             # Returns ""
```

**Hints:**
- Python has built-in ways to reverse strings
- Think about slicing with negative step
                """.strip(),
                cell_id="cell_2",
                points=8.0,
                starter_code="""def reverse_string(text):
    # TODO: Reverse the input string
    pass
"""
            ),
            Question(
                question_number=3,
                title="Find Maximum in List",
                description="""
## Task
Write a function `find_max(numbers)` that returns the largest number in a list.

**Requirements:**
- Return the maximum value from the list
- Handle lists with one element
- You can assume the list is not empty
- Do NOT use the built-in `max()` function

**Examples:**
```python
find_max([1, 5, 3, 9, 2])      # Returns 9
find_max([10])                  # Returns 10
find_max([-5, -2, -10, -1])    # Returns -1
find_max([42, 42, 42])         # Returns 42
```

**Hints:**
- Iterate through the list
- Keep track of the largest value seen so far
- Compare each element with the current maximum
                """.strip(),
                cell_id="cell_3",
                points=12.0,
                starter_code="""def find_max(numbers):
    # TODO: Find and return the maximum value
    # DO NOT use max() function
    pass
"""
            ),
            Question(
                question_number=4,
                title="Count Vowels",
                description="""
## Task
Write a function `count_vowels(text)` that counts the number of vowels (a, e, i, o, u) in a string.

**Requirements:**
- Count both uppercase and lowercase vowels
- Ignore all other characters
- Return an integer count

**Examples:**
```python
count_vowels("hello")          # Returns 2 (e, o)
count_vowels("AEIOU")          # Returns 5
count_vowels("Python")         # Returns 1 (o)
count_vowels("xyz")            # Returns 0
count_vowels("Education")      # Returns 5 (E, u, a, i, o)
```

**Hints:**
- Convert the string to lowercase for easier comparison
- Create a list or string of vowels to check against
- Loop through each character
                """.strip(),
                cell_id="cell_4",
                points=10.0,
                starter_code="""def count_vowels(text):
    # TODO: Count vowels in the string
    vowels = "aeiouAEIOU"
    pass
"""
            )
        ],
        teacher_id=teacher_id,
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    
    await assignment.insert()
    assignment_id = str(assignment.id)
    print(f"✅ Created assignment: {assignment.title}")
    print(f"   Assignment ID: {assignment_id}")
    print(f"   Questions: {len(assignment.questions)}")
    print(f"   Total Points: {sum(q.points for q in assignment.questions)}")
    
    # Create test cases for each question
    test_cases = []
    
    # Test cases for Question 1: Circle Area
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=1,
        cell_id="cell_1",
        testcase_name="Test Circle Area - Basic",
        testcase_function="""
def test_circle_area(student_code):
    # Execute student code
    exec(student_code, globals())
    
    # Test basic cases
    result1 = circle_area(5)
    assert abs(result1 - 78.53975) < 0.01, f"circle_area(5) should be ~78.54, got {result1}"
    
    result2 = circle_area(10)
    assert abs(result2 - 314.159) < 0.01, f"circle_area(10) should be ~314.16, got {result2}"
    
    result3 = circle_area(0)
    assert result3 == 0, f"circle_area(0) should be 0, got {result3}"
    
    return True, "All circle area tests passed!"
""",
        timeout=5,
        points=5.0,
        description="Test basic circle area calculations"
    ))
    
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=1,
        cell_id="cell_1",
        testcase_name="Test Circle Area - Edge Cases",
        testcase_function="""
def test_circle_area_edge(student_code):
    exec(student_code, globals())
    
    # Test edge cases
    result1 = circle_area(1)
    assert abs(result1 - 3.14159) < 0.01, f"circle_area(1) should be ~3.14, got {result1}"
    
    result2 = circle_area(100)
    assert abs(result2 - 31415.9) < 1, f"circle_area(100) should be ~31415.9, got {result2}"
    
    return True, "Edge case tests passed!"
""",
        timeout=5,
        points=5.0,
        description="Test edge cases for circle area"
    ))
    
    # Test cases for Question 2: Reverse String
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=2,
        cell_id="cell_2",
        testcase_name="Test String Reversal - Basic",
        testcase_function="""
def test_reverse_string(student_code):
    exec(student_code, globals())
    
    assert reverse_string("hello") == "olleh", "Failed: reverse_string('hello')"
    assert reverse_string("Python") == "nohtyP", "Failed: reverse_string('Python')"
    assert reverse_string("A B C") == "C B A", "Failed: reverse_string('A B C')"
    assert reverse_string("") == "", "Failed: reverse_string('')"
    
    return True, "String reversal tests passed!"
""",
        timeout=5,
        points=4.0,
        description="Test basic string reversal"
    ))
    
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=2,
        cell_id="cell_2",
        testcase_name="Test String Reversal - Special Characters",
        testcase_function="""
def test_reverse_special(student_code):
    exec(student_code, globals())
    
    assert reverse_string("Hello!") == "!olleH", "Failed with punctuation"
    assert reverse_string("12345") == "54321", "Failed with numbers"
    assert reverse_string("a") == "a", "Failed with single character"
    
    return True, "Special character tests passed!"
""",
        timeout=5,
        points=4.0,
        description="Test string reversal with special characters"
    ))
    
    # Test cases for Question 3: Find Maximum
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=3,
        cell_id="cell_3",
        testcase_name="Test Find Max - Basic",
        testcase_function="""
def test_find_max(student_code):
    exec(student_code, globals())
    
    assert find_max([1, 5, 3, 9, 2]) == 9, "Failed: find_max([1, 5, 3, 9, 2])"
    assert find_max([10]) == 10, "Failed: find_max([10])"
    assert find_max([-5, -2, -10, -1]) == -1, "Failed: find_max([-5, -2, -10, -1])"
    
    return True, "Find max basic tests passed!"
""",
        timeout=5,
        points=6.0,
        description="Test basic max finding"
    ))
    
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=3,
        cell_id="cell_3",
        testcase_name="Test Find Max - Advanced",
        testcase_function="""
def test_find_max_advanced(student_code):
    exec(student_code, globals())
    
    assert find_max([42, 42, 42]) == 42, "Failed with duplicate values"
    assert find_max([100, 50, 75, 25]) == 100, "Failed when max is first"
    assert find_max([1, 2, 3, 4, 5]) == 5, "Failed when max is last"
    
    return True, "Advanced max tests passed!"
""",
        timeout=5,
        points=6.0,
        description="Test advanced max scenarios"
    ))
    
    # Test cases for Question 4: Count Vowels
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=4,
        cell_id="cell_4",
        testcase_name="Test Count Vowels - Basic",
        testcase_function="""
def test_count_vowels(student_code):
    exec(student_code, globals())
    
    assert count_vowels("hello") == 2, "Failed: count_vowels('hello')"
    assert count_vowels("AEIOU") == 5, "Failed: count_vowels('AEIOU')"
    assert count_vowels("xyz") == 0, "Failed: count_vowels('xyz')"
    
    return True, "Vowel counting basic tests passed!"
""",
        timeout=5,
        points=5.0,
        description="Test basic vowel counting"
    ))
    
    test_cases.append(SingleCellTestCase(
        assignment_id=assignment_id,
        question_number=4,
        cell_id="cell_4",
        testcase_name="Test Count Vowels - Mixed Case",
        testcase_function="""
def test_count_vowels_mixed(student_code):
    exec(student_code, globals())
    
    assert count_vowels("Education") == 5, "Failed: count_vowels('Education')"
    assert count_vowels("Python") == 1, "Failed: count_vowels('Python')"
    assert count_vowels("HELLO world") == 3, "Failed: count_vowels('HELLO world')"
    
    return True, "Mixed case vowel tests passed!"
""",
        timeout=5,
        points=5.0,
        description="Test vowel counting with mixed case"
    ))
    
    # Insert all test cases
    for tc in test_cases:
        await tc.insert()
    
    print(f"\n✅ Created {len(test_cases)} test cases:")
    for tc in test_cases:
        print(f"   - Q{tc.question_number}: {tc.testcase_name} ({tc.points} pts)")
    
    total_test_points = sum(tc.points for tc in test_cases)
    print(f"\n📊 Summary:")
    print(f"   Total Assignment Points: {sum(q.points for q in assignment.questions)}")
    print(f"   Total Test Case Points: {total_test_points}")
    print(f"   Due Date: {assignment.due_date.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n✨ Sample assignment created successfully!")
    print(f"\n🎓 Students can now access this assignment at:")
    print(f"   /assignment/{assignment_id}/notebook")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_assignment())
