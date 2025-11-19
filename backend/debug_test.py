"""
Debug test to see actual error messages
"""
import requests

BASE_URL = "http://localhost:8000"

print("Testing teacher registration with detailed error...")
teacher_data = {
    "name": "Test Teacher",
    "email": "debug@test.com"
}

try:
    response = requests.post(f"{BASE_URL}/api/teacher/register", json=teacher_data)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Response Text: {response.text}")
    
    if response.headers.get('content-type') == 'application/json':
        print(f"JSON: {response.json()}")
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")
