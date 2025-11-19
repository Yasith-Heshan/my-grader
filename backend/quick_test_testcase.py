import requests
import json
from datetime import datetime, timedelta

# Step 0: Create a teacher first
print("Step 0: Creating teacher...")
teacher_url = "http://localhost:8000/api/teacher/register"
teacher_data = {
    "name": "Test Teacher",
    "email": f"teacher_{datetime.now().timestamp()}@test.com"
}

r = requests.post(teacher_url, json=teacher_data)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    teacher = r.json()
    teacher_id = teacher["_id"]
    print(f"✅ Teacher created with ID: {teacher_id}\n")
else:
    print(f"❌ Failed to create teacher: {r.json()}")
    exit(1)

# Step 1: Create an assignment
print("Step 1: Creating assignment...")
assignment_url = "http://localhost:8000/api/teacher/assignments"
assignment_data = {
    "teacher_id": teacher_id,
    "title": "Test Assignment",
    "description": "Test description",
    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
    "test_cases": []
}

r = requests.post(assignment_url, json=assignment_data)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    assignment = r.json()
    assignment_id = assignment["_id"]
    print(f"✅ Assignment created with ID: {assignment_id}\n")
else:
    print(f"❌ Failed to create assignment: {r.json()}")
    exit(1)

# Step 2: Create testcase for the assignment
print("Step 2: Creating testcase...")
testcase_url = "http://localhost:8000/api/teacher/testcases"
testcase_data = {
    "assignment_id": assignment_id,
    "question_number": 1,
    "cell_id": "cell_1",
    "testcase_name": "test_example",
    "testcase_function": "def test(s): return {'score': 1, 'feedback': 'ok'}",
    "timeout": 5,
    "language": "python",
    "points": 10
}

r = requests.post(testcase_url, json=testcase_data)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    testcase = r.json()
    testcase_id = testcase["_id"]
    print(f"✅ Testcase created:")
    print(json.dumps(testcase, indent=2))
    print()
else:
    print(f"❌ Failed to create testcase: {r.json()}")
    exit(1)

# Step 3: Get testcase by ID
print(f"Step 3: Getting testcase by ID ({testcase_id})...")
r = requests.get(f"{testcase_url}/{testcase_id}")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"✅ Retrieved testcase:")
    print(json.dumps(r.json(), indent=2))
    print()
else:
    print(f"❌ Failed: {r.json()}")

# Step 4: Get all testcases for assignment
print(f"Step 4: Getting all testcases for assignment...")
r = requests.get(f"http://localhost:8000/api/teacher/assignments/{assignment_id}/testcases")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    testcases = r.json()
    print(f"✅ Retrieved {len(testcases)} testcase(s)")
    print()
else:
    print(f"❌ Failed: {r.json()}")

# Step 5: Get testcases for specific cell
print(f"Step 5: Getting testcases for cell 'cell_1'...")
r = requests.get(f"http://localhost:8000/api/teacher/testcases/cell/{assignment_id}/cell_1")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    testcases = r.json()
    print(f"✅ Retrieved {len(testcases)} testcase(s) for cell 'cell_1'")
    print()
else:
    print(f"❌ Failed: {r.json()}")

print("="*60)
print("✅ All Task 1 endpoints tested successfully!")
print("="*60)

