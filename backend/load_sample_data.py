"""
Sample test data loader for the grading system
Loads teachers, students, assignments, and single-cell test cases
"""
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['grading_system']

print("🗑️  Clearing existing data...")
db.users.delete_many({})
db.assignments.delete_many({})
db.submissions.delete_many({})
db.single_cell_test_cases.delete_many({})
print("✅ Cleared all collections\n")

# Sample Teachers
print("👨‍🏫 Creating teachers...")
teachers = [
    {
        "_id": ObjectId(),
        "name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@university.edu",
        "role": "teacher",
        "created_at": datetime.utcnow()
    },
    {
        "_id": ObjectId(),
        "name": "Prof. Michael Chen",
        "email": "michael.chen@university.edu",
        "role": "teacher",
        "created_at": datetime.utcnow()
    }
]
db.users.insert_many(teachers)
print(f"✅ Created {len(teachers)} teachers\n")

# Sample Students
print("👨‍🎓 Creating students...")
students = [
    {
        "_id": ObjectId(),
        "name": "Alice Williams",
        "email": "alice.williams@student.edu",
        "student_id": "S001",
        "role": "student",
        "created_at": datetime.utcnow()
    },
    {
        "_id": ObjectId(),
        "name": "Bob Martinez",
        "email": "bob.martinez@student.edu",
        "student_id": "S002",
        "role": "student",
        "created_at": datetime.utcnow()
    },
    {
        "_id": ObjectId(),
        "name": "Charlie Davis",
        "email": "charlie.davis@student.edu",
        "student_id": "S003",
        "role": "student",
        "created_at": datetime.utcnow()
    }
]
db.users.insert_many(students)
print(f"✅ Created {len(students)} students\n")

# Sample Assignments
print("📝 Creating assignments...")
teacher_id = str(teachers[0]["_id"])

assignments = [
    {
        "_id": ObjectId(),
        "title": "Python Fundamentals - Functions and Loops",
        "description": """# Python Fundamentals Assignment

## Instructions
Complete the following Python functions. Each function should be written in its own code cell.

### Question 1: Circle Area Calculator
Write a function `circle_area(radius)` that calculates the area of a circle.

### Question 2: Factorial Function
Write a function `factorial(n)` that calculates the factorial of a number using recursion or loops.

### Question 3: List Operations
Write a function `filter_even(numbers)` that returns only even numbers from a list.

Make sure to test your code before submission!
""",
        "teacher_id": teacher_id,
        "due_date": datetime.utcnow() + timedelta(days=7),
        "max_score": 100,
        "test_cases": [
            {
                "id": "tc1",
                "name": "Basic Test",
                "input": "test input",
                "expected_output": "test output",
                "points": 10
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": ObjectId(),
        "title": "Data Structures - Lists and Dictionaries",
        "description": """# Data Structures Assignment

## Instructions
Work with Python lists and dictionaries.

### Question 1: Dictionary Operations
Write a function `count_words(text)` that counts word frequency in a string.

### Question 2: List Manipulation
Write a function `merge_sorted_lists(list1, list2)` that merges two sorted lists.

Each solution should be in a separate cell.
""",
        "teacher_id": teacher_id,
        "due_date": datetime.utcnow() + timedelta(days=14),
        "max_score": 80,
        "test_cases": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]
db.assignments.insert_many(assignments)
print(f"✅ Created {len(assignments)} assignments\n")

# Sample Single-Cell Test Cases
print("🧪 Creating single-cell test cases...")
assignment1_id = str(assignments[0]["_id"])
assignment2_id = str(assignments[1]["_id"])

test_cases = [
    # Assignment 1 - Question 1: Circle Area
    {
        "_id": ObjectId(),
        "assignment_id": assignment1_id,
        "question_number": 1,
        "cell_id": "cell-1",
        "testcase_name": "Test Circle Area - Basic",
        "testcase_function": """def test_circle_area(submission):
    '''Test the circle_area function with basic inputs'''
    import math
    
    if 'circle_area' not in submission:
        return {'score': 0.0, 'message': '❌ Function circle_area not found'}
    
    circle_area = submission['circle_area']
    
    # Test 1: radius = 5
    result1 = circle_area(5)
    expected1 = math.pi * 5 ** 2
    
    if abs(result1 - expected1) < 0.001:
        return {'score': 1.0, 'message': '✅ Perfect! circle_area(5) = ' + str(result1)}
    else:
        return {'score': 0.0, 'message': f'❌ Expected {expected1:.4f}, got {result1:.4f}'}
""",
        "description": "Tests circle_area function with radius 5",
        "points": 20,
        "timeout": 5,
        "language": "python",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": ObjectId(),
        "assignment_id": assignment1_id,
        "question_number": 1,
        "cell_id": "cell-1",
        "testcase_name": "Test Circle Area - Edge Cases",
        "testcase_function": """def test_circle_area_edge(submission):
    '''Test the circle_area function with edge cases'''
    import math
    
    if 'circle_area' not in submission:
        return {'score': 0.0, 'message': '❌ Function circle_area not found'}
    
    circle_area = submission['circle_area']
    
    # Test with radius = 0
    result = circle_area(0)
    if result != 0:
        return {'score': 0.0, 'message': f'❌ circle_area(0) should be 0, got {result}'}
    
    # Test with radius = 10
    result = circle_area(10)
    expected = math.pi * 100
    if abs(result - expected) < 0.001:
        return {'score': 1.0, 'message': '✅ All edge cases passed!'}
    else:
        return {'score': 0.5, 'message': f'⚠️ Partial: Some tests failed'}
""",
        "description": "Tests circle_area with edge cases (0, large numbers)",
        "points": 10,
        "timeout": 5,
        "language": "python",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    
    # Assignment 1 - Question 2: Factorial
    {
        "_id": ObjectId(),
        "assignment_id": assignment1_id,
        "question_number": 2,
        "cell_id": "cell-2",
        "testcase_name": "Test Factorial Function",
        "testcase_function": """def test_factorial(submission):
    '''Test the factorial function'''
    
    if 'factorial' not in submission:
        return {'score': 0.0, 'message': '❌ Function factorial not found'}
    
    factorial = submission['factorial']
    
    # Test cases
    test_cases = [
        (0, 1),
        (1, 1),
        (5, 120),
        (7, 5040)
    ]
    
    passed = 0
    total = len(test_cases)
    
    for n, expected in test_cases:
        try:
            result = factorial(n)
            if result == expected:
                passed += 1
        except:
            pass
    
    score = passed / total
    if score == 1.0:
        return {'score': 1.0, 'message': f'✅ Perfect! All {total} tests passed'}
    elif score > 0:
        return {'score': score, 'message': f'⚠️ Partial: {passed}/{total} tests passed'}
    else:
        return {'score': 0.0, 'message': '❌ No tests passed'}
""",
        "description": "Tests factorial function with multiple inputs",
        "points": 25,
        "timeout": 5,
        "language": "python",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    
    # Assignment 1 - Question 3: Filter Even
    {
        "_id": ObjectId(),
        "assignment_id": assignment1_id,
        "question_number": 3,
        "cell_id": "cell-3",
        "testcase_name": "Test Filter Even Numbers",
        "testcase_function": """def test_filter_even(submission):
    '''Test the filter_even function'''
    
    if 'filter_even' not in submission:
        return {'score': 0.0, 'message': '❌ Function filter_even not found'}
    
    filter_even = submission['filter_even']
    
    # Test cases
    tests = [
        ([1, 2, 3, 4, 5, 6], [2, 4, 6]),
        ([1, 3, 5, 7], []),
        ([2, 4, 6, 8], [2, 4, 6, 8]),
        ([], [])
    ]
    
    passed = 0
    for input_list, expected in tests:
        try:
            result = filter_even(input_list)
            if result == expected:
                passed += 1
        except:
            pass
    
    score = passed / len(tests)
    if score == 1.0:
        return {'score': 1.0, 'message': '✅ Perfect! All test cases passed'}
    elif score > 0:
        return {'score': score, 'message': f'⚠️ {passed}/{len(tests)} tests passed'}
    else:
        return {'score': 0.0, 'message': '❌ Failed all tests'}
""",
        "description": "Tests filter_even with various lists",
        "points": 15,
        "timeout": 5,
        "language": "python",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    
    # Assignment 2 - Question 1: Count Words
    {
        "_id": ObjectId(),
        "assignment_id": assignment2_id,
        "question_number": 1,
        "cell_id": "cell-1",
        "testcase_name": "Test Word Counter",
        "testcase_function": """def test_count_words(submission):
    '''Test the count_words function'''
    
    if 'count_words' not in submission:
        return {'score': 0.0, 'message': '❌ Function count_words not found'}
    
    count_words = submission['count_words']
    
    # Test case
    text = "hello world hello python world"
    result = count_words(text)
    expected = {'hello': 2, 'world': 2, 'python': 1}
    
    if result == expected:
        return {'score': 1.0, 'message': '✅ Perfect! Word counting works correctly'}
    else:
        return {'score': 0.0, 'message': f'❌ Expected {expected}, got {result}'}
""",
        "description": "Tests word frequency counter",
        "points": 20,
        "timeout": 5,
        "language": "python",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    
    # Assignment 2 - Question 2: Merge Lists
    {
        "_id": ObjectId(),
        "assignment_id": assignment2_id,
        "question_number": 2,
        "cell_id": "cell-2",
        "testcase_name": "Test Merge Sorted Lists",
        "testcase_function": """def test_merge_sorted_lists(submission):
    '''Test the merge_sorted_lists function'''
    
    if 'merge_sorted_lists' not in submission:
        return {'score': 0.0, 'message': '❌ Function merge_sorted_lists not found'}
    
    merge = submission['merge_sorted_lists']
    
    # Test cases
    tests = [
        ([1, 3, 5], [2, 4, 6], [1, 2, 3, 4, 5, 6]),
        ([1, 2, 3], [], [1, 2, 3]),
        ([], [1, 2], [1, 2])
    ]
    
    passed = 0
    for list1, list2, expected in tests:
        try:
            result = merge(list1, list2)
            if result == expected:
                passed += 1
        except:
            pass
    
    score = passed / len(tests)
    if score == 1.0:
        return {'score': 1.0, 'message': '✅ All merge tests passed!'}
    else:
        return {'score': score, 'message': f'⚠️ {passed}/{len(tests)} tests passed'}
""",
        "description": "Tests merging of sorted lists",
        "points": 25,
        "timeout": 5,
        "language": "python",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

db.single_cell_test_cases.insert_many(test_cases)
print(f"✅ Created {len(test_cases)} single-cell test cases\n")

# Sample Student Submissions
print("📤 Creating sample submissions...")
submissions = [
    # Alice's submission - Correct implementation
    {
        "_id": ObjectId(),
        "assignment_id": assignment1_id,
        "student_id": str(students[0]["_id"]),
        "code": """import math

def circle_area(radius):
    return math.pi * radius ** 2

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def filter_even(numbers):
    return [n for n in numbers if n % 2 == 0]
""",
        "submitted_at": datetime.utcnow() - timedelta(days=1),
        "graded": True,
        "score": 95,
        "feedback": "Excellent work! All functions implemented correctly.",
        "graded_at": datetime.utcnow()
    },
    
    # Bob's submission - Partial implementation
    {
        "_id": ObjectId(),
        "assignment_id": assignment1_id,
        "student_id": str(students[1]["_id"]),
        "code": """def circle_area(radius):
    return 3.14 * radius * radius  # Not using math.pi

def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

# filter_even not implemented yet
""",
        "submitted_at": datetime.utcnow() - timedelta(hours=12),
        "graded": False,
        "score": 0
    }
]

db.submissions.insert_many(submissions)
print(f"✅ Created {len(submissions)} sample submissions\n")

# Print Summary
print("\n" + "="*60)
print("📊 SAMPLE DATA SUMMARY")
print("="*60)
print(f"Teachers: {len(teachers)}")
for t in teachers:
    print(f"  - {t['name']} ({t['email']})")

print(f"\nStudents: {len(students)}")
for s in students:
    print(f"  - {s['name']} ({s['email']})")

print(f"\nAssignments: {len(assignments)}")
for i, a in enumerate(assignments, 1):
    print(f"  {i}. {a['title']}")
    print(f"     ID: {a['_id']}")
    testcase_count = db.single_cell_test_cases.count_documents({"assignment_id": str(a['_id'])})
    print(f"     Test Cases: {testcase_count}")

print(f"\nTotal Test Cases: {len(test_cases)}")
print(f"Total Submissions: {len(submissions)}")

print("\n" + "="*60)
print("✅ Sample data loaded successfully!")
print("="*60)
print("\n📝 Login Credentials (any password works):")
print("\nTeacher:")
print("  Email: sarah.johnson@university.edu")
print("  Role: Teacher")
print("\nStudent:")
print("  Email: alice.williams@student.edu")
print("  Role: Student")
print("\n🌐 Frontend: http://localhost:3000")
print("🔧 Backend: http://localhost:8000/docs")
