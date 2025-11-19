import requests

# Replace with your actual assignment_id from the database
ASSIGNMENT_ID = "YOUR_ASSIGNMENT_ID_HERE"
BASE_URL = "http://localhost:8000/api"

print("Testing Cell Evaluation\n")

# Test 1: Correct implementation
print("1. Testing CORRECT implementation:")
response = requests.post(f"{BASE_URL}/student/evaluate-cell", json={
    "assignment_id": ASSIGNMENT_ID,
    "cell_id": "cell-1",
    "student_code": """
def circle_area(radius):
    import math
    return math.pi * radius ** 2
"""
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: Incorrect implementation
print("2. Testing INCORRECT implementation:")
response = requests.post(f"{BASE_URL}/student/evaluate-cell", json={
    "assignment_id": ASSIGNMENT_ID,
    "cell_id": "cell-1",
    "student_code": """
def circle_area(radius):
    return 3.14 * radius  # Wrong formula
"""
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 3: Missing function
print("3. Testing MISSING function:")
response = requests.post(f"{BASE_URL}/student/evaluate-cell", json={
    "assignment_id": ASSIGNMENT_ID,
    "cell_id": "cell-1",
    "student_code": """
# No function defined
x = 5
"""
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")
