import requests
from pymongo import MongoClient

# Get assignment ID from database
client = MongoClient('mongodb://localhost:27017/')
db = client['grading_system']
assignment = db.assignments.find_one()

if not assignment:
    print("No assignments found. Please create one first!")
    exit(1)

assignment_id = str(assignment['_id'])
print(f"Using assignment ID: {assignment_id}")
print(f"Assignment: {assignment['title']}\n")

# Check if testcases exist
testcases = list(db.single_cell_test_cases.find({'assignment_id': assignment_id, 'cell_id': 'cell-1'}))
if not testcases:
    print("⚠️ No testcases found for cell-1. Please create one first in the UI!")
    print("Go to: Teacher Dashboard → View Submissions → Cell Test Cases tab")
    exit(1)

print(f"Found {len(testcases)} testcase(s) for cell-1\n")

BASE_URL = "http://localhost:8000/api"

print("=" * 60)
print("Testing Cell Evaluation")
print("=" * 60)

# Test 1: Correct implementation
print("\n✅ Test 1: CORRECT implementation")
print("-" * 60)
response = requests.post(f"{BASE_URL}/student/evaluate-cell", json={
    "assignment_id": assignment_id,
    "cell_id": "cell-1",
    "student_code": """
def circle_area(radius):
    import math
    return math.pi * radius ** 2
"""
})
print(f"Status: {response.status_code}")
result = response.json()
print(f"Score: {result['score']}/{result['total_points']}")
print(f"Feedback: {result['feedback']}")
print(f"Execution Time: {result['execution_time_ms']}ms")

# Test 2: Incorrect implementation
print("\n❌ Test 2: INCORRECT implementation")
print("-" * 60)
response = requests.post(f"{BASE_URL}/student/evaluate-cell", json={
    "assignment_id": assignment_id,
    "cell_id": "cell-1",
    "student_code": """
def circle_area(radius):
    return 3.14 * radius  # Wrong formula
"""
})
print(f"Status: {response.status_code}")
result = response.json()
print(f"Score: {result['score']}/{result['total_points']}")
print(f"Feedback: {result['feedback']}")
print(f"Execution Time: {result['execution_time_ms']}ms")

# Test 3: Missing function
print("\n⚠️ Test 3: MISSING function")
print("-" * 60)
response = requests.post(f"{BASE_URL}/student/evaluate-cell", json={
    "assignment_id": assignment_id,
    "cell_id": "cell-1",
    "student_code": """
# No function defined
x = 5
"""
})
print(f"Status: {response.status_code}")
result = response.json()
print(f"Score: {result['score']}/{result['total_points']}")
print(f"Feedback: {result['feedback']}")
print(f"Execution Time: {result['execution_time_ms']}ms")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
