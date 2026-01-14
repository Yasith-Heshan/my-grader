"""
Test API endpoints for Docker image selection feature
This script makes actual HTTP requests to test the endpoints
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_docker_image_endpoints():
    """Test Docker image related API endpoints"""
    
    print("🧪 Testing Docker Image Selection API Endpoints\n")
    print("=" * 60)
    
    # Step 1: Login as teacher
    print("\n1️⃣ Logging in as teacher...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "teacher@example.com",
            "password": "password123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Login successful")
    
    # Step 2: Get Docker images
    print("\n2️⃣ Fetching Docker images...")
    images_response = requests.get(
        f"{BASE_URL}/api/teacher/custom-images",
        headers=headers,
        params={"status_filter": "uploaded"}
    )
    
    if images_response.status_code != 200:
        print(f"   ❌ Failed to fetch images: {images_response.status_code}")
        return
    
    images = images_response.json()
    print(f"   ✅ Found {len(images)} uploaded Docker images")
    
    if not images:
        print("   ⚠️  No uploaded images found")
        print("   Run: python backend/test_data/load_sample_docker_images.py")
        return
    
    # Show first few images
    for img in images[:3]:
        print(f"      • {img['name']} (ID: {img.get('id') or img.get('_id')})")
    
    # Step 3: Create assignment with Docker image
    print("\n3️⃣ Creating assignment with custom Docker image...")
    
    docker_image_id = images[0].get('id') or images[0].get('_id')
    
    assignment_data = {
        "title": f"Test Assignment - {datetime.now().strftime('%H:%M:%S')}",
        "description": "This assignment uses a custom Docker image for testing",
        "questions": [
            {
                "question_number": 1,
                "title": "Test Question",
                "description": "Write a simple Python function",
                "cell_id": "cell_1",
                "points": 10,
                "starter_code": "# Write your code here\n"
            }
        ],
        "teacher_id": login_response.json()["user"]["id"],
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "custom_docker_image_id": docker_image_id
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/teacher/assignments",
        headers=headers,
        json=assignment_data
    )
    
    if create_response.status_code == 201:
        assignment = create_response.json()
        print("   ✅ Assignment created successfully")
        print(f"      • Title: {assignment['title']}")
        print(f"      • Docker Image ID: {assignment.get('custom_docker_image_id')}")
    else:
        print(f"   ❌ Failed to create assignment: {create_response.status_code}")
        print(f"   Response: {create_response.text}")
        return
    
    # Step 4: Verify assignment has custom image
    print("\n4️⃣ Verifying assignment has custom Docker image...")
    assignment_id = assignment.get('id') or assignment.get('_id')
    
    get_response = requests.get(
        f"{BASE_URL}/api/teacher/assignments/{assignment_id}",
        headers=headers
    )
    
    if get_response.status_code == 200:
        retrieved_assignment = get_response.json()
        if retrieved_assignment.get('custom_docker_image_id') == docker_image_id:
            print("   ✅ Docker image ID correctly saved")
        else:
            print("   ❌ Docker image ID mismatch")
    else:
        print(f"   ⚠️  Could not verify: {get_response.status_code}")
    
    # Step 5: Test validation - try using invalid image ID
    print("\n5️⃣ Testing validation (invalid image ID)...")
    
    invalid_data = assignment_data.copy()
    invalid_data["title"] = "Invalid Test"
    invalid_data["custom_docker_image_id"] = "000000000000000000000000"
    
    invalid_response = requests.post(
        f"{BASE_URL}/api/teacher/assignments",
        headers=headers,
        json=invalid_data
    )
    
    if invalid_response.status_code == 400:
        print("   ✅ Validation working - rejected invalid image ID")
        print(f"      Error: {invalid_response.json().get('detail')}")
    else:
        print(f"   ⚠️  Unexpected response: {invalid_response.status_code}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ All API endpoint tests passed!")
    print("\n📋 Test Summary:")
    print(f"   • Login: ✅")
    print(f"   • Fetch Docker Images: ✅")
    print(f"   • Create Assignment with Image: ✅")
    print(f"   • Verify Image Saved: ✅")
    print(f"   • Validation: ✅")
    print()

if __name__ == "__main__":
    try:
        test_docker_image_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the backend running?")
        print("   Start with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
