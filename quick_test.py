"""
Quick test script - tests the API endpoints directly
Run this while the server is running in a separate terminal
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register_teacher():
    print("\n=== Testing Teacher Registration ===")
    teacher_data = {
        "name": "Test Teacher",
        "email": f"teacher_{int(time.time())}@test.com"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/teacher/register", json=teacher_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            return response.json()['_id']
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_register_student():
    print("\n=== Testing Student Registration ===")
    student_data = {
        "name": "Test Student",
        "email": f"student_{int(time.time())}@test.com",
        "student_number": f"S{int(time.time())}"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/student/register", json=student_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            return response.json()['_id']
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_create_assignment(teacher_id):
    print("\n=== Testing Assignment Creation ===")
    assignment_data = {
        "teacher_id": teacher_id,
        "title": "Test Assignment",
        "description": "A test assignment",
        "due_date": "2025-12-31T23:59:59"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/teacher/assignments", json=assignment_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        if response.status_code == 201:
            return response.json()['_id']
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("QUICK API TEST")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n[ERROR] Server is not running or not responding!")
        print("Please start the server with: python main.py")
        exit(1)
    
    print("\n[OK] Server is healthy!")
    
    # Test teacher registration
    teacher_id = test_register_teacher()
    if teacher_id:
        print(f"\n[OK] Teacher created with ID: {teacher_id}")
    else:
        print("\n[ERROR] Failed to create teacher")
    
    # Test student registration
    student_id = test_register_student()
    if student_id:
        print(f"\n[OK] Student created with ID: {student_id}")
    else:
        print("\n[ERROR] Failed to create student")
    
    # Test assignment creation
    if teacher_id:
        assignment_id = test_create_assignment(teacher_id)
        if assignment_id:
            print(f"\n[OK] Assignment created with ID: {assignment_id}")
        else:
            print("\n[ERROR] Failed to create assignment")
    
    print("\n" + "=" * 60)
    print("QUICK TEST COMPLETE")
    print("=" * 60)
    print("\nFor full test with grading, run: python test_data\\load_test_data.py")
