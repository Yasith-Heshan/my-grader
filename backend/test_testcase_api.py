"""
Test script for single-cell testcase API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/teacher"

def test_create_testcase():
    """Test creating a single-cell testcase"""
    print("\n" + "="*60)
    print("TEST 1: Create Single-Cell Testcase")
    print("="*60)
    
    # First, we need an assignment ID. Let's create one or use existing
    testcase_data = {
        "assignment_id": "507f1f77bcf86cd799439011",  # Placeholder ID
        "question_number": 1,
        "cell_id": "cell_1",
        "testcase_name": "test_circle_area",
        "testcase_function": """def test_circle_area(submission):
    import math
    if 'circle_area' not in submission:
        return {"score": 0, "feedback": "Function 'circle_area' not found"}
    
    func = submission['circle_area']
    test_cases = [
        (1, math.pi),
        (3, 9 * math.pi),
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
                feedback_parts.append(f"❌ Wrong for radius={radius}")
        except Exception as e:
            feedback_parts.append(f"❌ Error: {str(e)}")
    
    final_score = score / len(test_cases)
    feedback = "\\n".join(feedback_parts)
    return {"score": final_score, "feedback": feedback}
""",
        "test_args": None,
        "expected_output": None,
        "timeout": 5,
        "language": "python",
        "points": 10.0,
        "description": "Test circle area calculation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/testcases", json=testcase_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Testcase created successfully!")
            return response.json()["_id"]
        else:
            print("❌ Failed to create testcase")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_get_testcase(testcase_id):
    """Test getting a testcase by ID"""
    print("\n" + "="*60)
    print("TEST 2: Get Testcase by ID")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/testcases/{testcase_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Testcase retrieved successfully!")
        else:
            print("❌ Failed to retrieve testcase")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_assignment_testcases():
    """Test getting all testcases for an assignment"""
    print("\n" + "="*60)
    print("TEST 3: Get All Testcases for Assignment")
    print("="*60)
    
    assignment_id = "507f1f77bcf86cd799439011"
    
    try:
        response = requests.get(f"{BASE_URL}/assignments/{assignment_id}/testcases")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            testcases = response.json()
            print(f"✅ Retrieved {len(testcases)} testcase(s)!")
        else:
            print("❌ Failed to retrieve testcases")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_cell_testcases():
    """Test getting testcases for a specific cell"""
    print("\n" + "="*60)
    print("TEST 4: Get Testcases for Specific Cell")
    print("="*60)
    
    assignment_id = "507f1f77bcf86cd799439011"
    cell_id = "cell_1"
    
    try:
        response = requests.get(f"{BASE_URL}/testcases/cell/{assignment_id}/{cell_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            testcases = response.json()
            print(f"✅ Retrieved {len(testcases)} testcase(s) for cell '{cell_id}'!")
        else:
            print("❌ Failed to retrieve cell testcases")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health():
    """Test if server is running"""
    print("\n" + "="*60)
    print("HEALTH CHECK")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Server is healthy!")
            return True
        else:
            print("❌ Server health check failed")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🧪 Testing Single-Cell Testcase API Endpoints")
    print("Make sure the server is running on http://localhost:8000\n")
    
    # Check server health
    if not test_health():
        print("\n❌ Server is not running. Please start it first.")
        exit(1)
    
    # Run tests
    testcase_id = test_create_testcase()
    
    if testcase_id:
        test_get_testcase(testcase_id)
    
    test_get_assignment_testcases()
    test_get_cell_testcases()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
