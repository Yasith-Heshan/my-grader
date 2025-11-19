"""
Test the single-cell evaluation endpoint
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Step 1: Create teacher
print("Step 1: Creating teacher...")
teacher_data = {"name": "Test Teacher", "email": f"teacher_{datetime.now().timestamp()}@test.com"}
r = requests.post(f"{BASE_URL}/api/teacher/register", json=teacher_data)
teacher_id = r.json()["_id"]
print(f"✅ Teacher created: {teacher_id}\n")

# Step 2: Create assignment
print("Step 2: Creating assignment...")
assignment_data = {
    "teacher_id": teacher_id,
    "title": "Python Functions Assignment",
    "description": "Test your circle_area function",
    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
    "test_cases": []
}
r = requests.post(f"{BASE_URL}/api/teacher/assignments", json=assignment_data)
assignment_id = r.json()["_id"]
print(f"✅ Assignment created: {assignment_id}\n")

# Step 3: Create testcase with the sample function
print("Step 3: Creating testcase...")
testcase_data = {
    "assignment_id": assignment_id,
    "question_number": 1,
    "cell_id": "cell_1",
    "testcase_name": "test_circle_area",
    "testcase_function": """def test_circle_area(submission):
    import math
    if 'circle_area' not in submission:
        return {"score": 0, "feedback": "❌ Function 'circle_area' not found!"}
    
    func = submission['circle_area']
    test_cases = [
        (1, math.pi),
        (3, 9 * math.pi),
        (0, 0),
        (5.5, 30.25 * math.pi)
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
                feedback_parts.append(f"❌ Wrong for radius={radius}: got {result}, expected {expected:.3f}")
        except Exception as e:
            feedback_parts.append(f"❌ Error for radius={radius}: {str(e)}")
    
    final_score = score / len(test_cases)
    feedback = f"Circle Area Test: {score}/{len(test_cases)} test cases passed\\n" + "\\n".join(feedback_parts)
    return {"score": final_score, "feedback": feedback}
""",
    "timeout": 5,
    "language": "python",
    "points": 10.0,
    "description": "Test circle area calculation"
}
r = requests.post(f"{BASE_URL}/api/teacher/testcases", json=testcase_data)
print(f"✅ Testcase created\n")

# Step 4: Test with CORRECT student code
print("Step 4: Evaluating CORRECT student code...")
print("="*60)
correct_code = """
import math

def circle_area(radius):
    '''Calculate the area of a circle given its radius'''
    return math.pi * radius ** 2
"""

eval_request = {
    "assignment_id": assignment_id,
    "cell_id": "cell_1",
    "student_code": correct_code
}

r = requests.post(f"{BASE_URL}/api/student/evaluate-cell", json=eval_request)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"\n✅ Evaluation succeeded!")
    print(f"Score: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
    print(f"Passed: {result['passed_tests']}/{result['total_tests']} tests")
    print(f"\nFeedback: {result['feedback']}")
    if result['results']:
        print(f"\nDetailed Results:")
        for test in result['results']:
            print(f"  - {test['testcase_name']}: {test['score']}/{test['max_score']}")
            print(f"    {test['feedback']}")
else:
    print(f"❌ Failed: {r.json()}")

# Step 5: Test with INCORRECT student code
print("\n\nStep 5: Evaluating INCORRECT student code...")
print("="*60)
incorrect_code = """
def circle_area(radius):
    '''Calculate the area of a circle - BUT WRONG!'''
    return radius * 2  # Wrong formula!
"""

eval_request = {
    "assignment_id": assignment_id,
    "cell_id": "cell_1",
    "student_code": incorrect_code
}

r = requests.post(f"{BASE_URL}/api/student/evaluate-cell", json=eval_request)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"\n✅ Evaluation succeeded!")
    print(f"Score: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
    print(f"Passed: {result['passed_tests']}/{result['total_tests']} tests")
    print(f"\nFeedback: {result['feedback']}")
    if result['results']:
        print(f"\nDetailed Results:")
        for test in result['results']:
            print(f"  - {test['testcase_name']}: {test['score']}/{test['max_score']}")
            print(f"    {test['feedback']}")
else:
    print(f"❌ Failed: {r.json()}")

# Step 6: Test with MISSING function
print("\n\nStep 6: Evaluating code with MISSING function...")
print("="*60)
missing_code = """
# Student forgot to write the function!
x = 42
"""

eval_request = {
    "assignment_id": assignment_id,
    "cell_id": "cell_1",
    "student_code": missing_code
}

r = requests.post(f"{BASE_URL}/api/student/evaluate-cell", json=eval_request)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"\n✅ Evaluation succeeded!")
    print(f"Score: {result['score']}/{result['max_score']} ({result['percentage']:.1f}%)")
    print(f"Passed: {result['passed_tests']}/{result['total_tests']} tests")
    print(f"\nFeedback: {result['feedback']}")
    if result['results']:
        print(f"\nDetailed Results:")
        for test in result['results']:
            print(f"  - {test['testcase_name']}: {test['score']}/{test['max_score']}")
            print(f"    {test['feedback']}")
else:
    print(f"❌ Failed: {r.json()}")

print("\n" + "="*60)
print("✅ All evaluation tests completed!")
print("="*60)
