"""
Quick test script to verify MongoDB setup and API
Run this after starting the server to test basic functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if server is running"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Status: {response.status_code}")
    print(f"📊 Response: {response.json()}\n")
    return response.status_code == 200

def test_teacher_registration():
    """Test teacher registration"""
    print("👨‍🏫 Testing teacher registration...")
    data = {
        "name": "Dr. Test Teacher",
        "email": "test.teacher@university.edu"
    }
    response = requests.post(f"{BASE_URL}/api/teacher/register", json=data)
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Teacher ID: {result.get('_id')}\n")
    return result.get('_id') if response.status_code == 201 else None

def test_student_registration():
    """Test student registration"""
    print("👨‍🎓 Testing student registration...")
    data = {
        "name": "Alice Test Student",
        "email": "alice.test@student.edu",
        "student_number": "TEST001"
    }
    response = requests.post(f"{BASE_URL}/api/student/register", json=data)
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Student ID: {result.get('_id')}\n")
    return result.get('_id') if response.status_code == 201 else None

def test_create_assignment(teacher_id):
    """Test assignment creation"""
    print("📝 Testing assignment creation...")
    data = {
        "title": "Test Assignment - Python Basics",
        "description": "A test assignment for system validation",
        "teacher_id": teacher_id
    }
    response = requests.post(f"{BASE_URL}/api/teacher/assignments", json=data)
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Assignment ID: {result.get('_id')}\n")
    return result.get('_id') if response.status_code == 201 else None

def test_add_test_case(assignment_id):
    """Test adding test cases"""
    print("🧪 Testing test case addition...")
    data = {
        "test_cases": [
            {
                "question_number": 1,
                "cell_id": "cell_1",
                "test_code": "passed = 'result' in locals() and result == 42\nfeedback = 'Correct!' if passed else 'Expected 42'",
                "points": 10.0,
                "description": "Calculate 6 * 7"
            }
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/teacher/assignments/{assignment_id}/questions",
        json=data
    )
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Test Cases Created: {len(result)}\n")
    return result[0].get('_id') if response.status_code == 201 and result else None

def test_create_submission(assignment_id, student_id):
    """Test submission creation"""
    print("📤 Testing submission creation...")
    data = {
        "assignment_id": assignment_id,
        "student_id": student_id
    }
    response = requests.post(f"{BASE_URL}/api/student/submissions", json=data)
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Submission ID: {result.get('_id')}\n")
    return result.get('_id') if response.status_code == 201 else None

def test_submit_code(submission_id, test_case_id):
    """Test code submission"""
    print("💻 Testing code submission...")
    data = {
        "test_case_id": test_case_id,
        "cell_id": "cell_1",
        "submitted_code": "result = 6 * 7"
    }
    response = requests.post(
        f"{BASE_URL}/api/student/submissions/{submission_id}/items",
        json=data
    )
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Submission Item ID: {result.get('_id')}\n")
    return response.status_code == 201

def test_grade_assignment(assignment_id):
    """Test grading"""
    print("📊 Testing grading...")
    response = requests.post(f"{BASE_URL}/api/teacher/assignments/{assignment_id}/grade")
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Grading Result: {result}\n")
    return response.status_code == 200

def test_view_results(submission_id):
    """Test viewing results"""
    print("📈 Testing result retrieval...")
    response = requests.get(f"{BASE_URL}/api/student/submissions/{submission_id}/results")
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    print(f"📊 Score: {result.get('total_score')}/{result.get('max_score')}")
    print(f"📊 Percentage: {result.get('percentage'):.1f}%")
    print(f"📊 Status: {result.get('status')}\n")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Starting System Tests")
    print("="*60 + "\n")
    
    try:
        # Test 1: Health check
        if not test_health_check():
            print("❌ Server is not responding. Please start the server first.")
            return
        
        # Test 2: Register teacher
        teacher_id = test_teacher_registration()
        if not teacher_id:
            print("❌ Teacher registration failed")
            return
        
        # Test 3: Register student
        student_id = test_student_registration()
        if not student_id:
            print("❌ Student registration failed")
            return
        
        # Test 4: Create assignment
        assignment_id = test_create_assignment(teacher_id)
        if not assignment_id:
            print("❌ Assignment creation failed")
            return
        
        # Test 5: Add test case
        test_case_id = test_add_test_case(assignment_id)
        if not test_case_id:
            print("❌ Test case addition failed")
            return
        
        # Test 6: Create submission
        submission_id = test_create_submission(assignment_id, student_id)
        if not submission_id:
            print("❌ Submission creation failed")
            return
        
        # Test 7: Submit code
        if not test_submit_code(submission_id, test_case_id):
            print("❌ Code submission failed")
            return
        
        # Test 8: Grade assignment
        if not test_grade_assignment(assignment_id):
            print("❌ Grading failed")
            return
        
        # Test 9: View results
        if not test_view_results(submission_id):
            print("❌ Result retrieval failed")
            return
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎉 The grading system is working correctly with MongoDB!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server.")
        print("Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()
